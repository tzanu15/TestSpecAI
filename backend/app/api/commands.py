"""
API endpoints for GenericCommand and CommandCategory management.

This module provides RESTful endpoints for managing generic commands, command categories,
and command-parameter relationships with proper validation, error handling, and documentation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud.command import generic_command
from app.crud.category import command_category
from app.schemas.command import (
    GenericCommandCreate,
    GenericCommandUpdate,
    GenericCommandResponse,
    GenericCommandListResponse,
    CommandCategoryCreate,
    CommandCategoryUpdate,
    CommandCategoryResponse
)
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
from app.crud.transaction_manager import transaction_context, execute_in_transaction
from app.crud.advanced_queries import FilterCondition, FilterOperator, SortCondition, SortDirection, PaginationParams, SearchParams
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Generic Command Management Endpoints

@router.get("/", response_model=GenericCommandListResponse)
async def get_commands(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category_id: Optional[str] = Query(None, description="Filter by command category ID"),
    search: Optional[str] = Query(None, description="Search commands by template content"),
    has_parameters: Optional[bool] = Query(None, description="Filter by commands with/without parameters"),
    sort_by: str = Query("created_at", description="Sort by field (template, created_at, updated_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    include_category: bool = Query(True, description="Include category information in response"),
    include_parameters: bool = Query(False, description="Include required parameters in response")
):
    """
    Get all generic commands with advanced filtering, sorting, and pagination.

    **Filtering Options:**
    - category_id: Filter by command category ID
    - search: Search by template content (case-insensitive partial match)
    - has_parameters: Filter by commands with/without parameters (true/false)
    - is_active: Filter by active status (default: true)
    - created_by: Filter by creator username

    **Sorting Options:**
    - sort_by: Sort by field (template, created_at, updated_at) - default: created_at
    - sort_order: Sort order (asc, desc) - default: desc

    **Response Options:**
    - include_category: Include category information in response (default: true)
    - include_parameters: Include required parameters in response (default: false)

    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)

    **Example Requests:**
    - Get all commands: GET /commands/
    - Search commands: GET /commands/?search=authentication
    - Filter by category: GET /commands/?category_id=123&has_parameters=true
    - Sort by template: GET /commands/?sort_by=template&sort_order=asc
    - Include parameters: GET /commands/?include_parameters=true
    """
    try:
        # Build advanced filters
        filters = []

        if category_id:
            filters.append(FilterCondition("category_id", FilterOperator.EQ, category_id))

        if is_active is not None:
            filters.append(FilterCondition("is_active", FilterOperator.EQ, is_active))

        if created_by:
            filters.append(FilterCondition("created_by", FilterOperator.EQ, created_by))

        # Build sort conditions
        sorts = []
        if sort_by in ["template", "created_at", "updated_at"]:
            sort_direction = SortDirection.ASC if sort_order.lower() == "asc" else SortDirection.DESC
            sorts.append(SortCondition(sort_by, sort_direction))

        # Build search parameters
        search_params = None
        if search:
            search_params = SearchParams(
                search_term=search,
                search_fields=["template", "description"]
            )

        # Build pagination parameters
        pagination = PaginationParams(skip=skip, limit=limit)

        # Get commands using advanced queries
        if has_parameters is not None:
            if has_parameters:
                # Get parameterized commands
                commands = await generic_command.get_parameterized_commands(
                    db, skip=skip, limit=limit
                )
                total = len(commands)  # This is a simplified count
            else:
                # Get simple commands
                commands = await generic_command.get_simple_commands(
                    db, skip=skip, limit=limit
                )
                total = len(commands)  # This is a simplified count
        elif search:
            # Search by template
            commands = await generic_command.search_by_template(
                db, template=search, skip=skip, limit=limit
            )
            total = len(commands)  # This is a simplified count
        elif category_id:
            # Get by category
            commands = await generic_command.get_by_category(
                db, category_id=category_id, skip=skip, limit=limit
            )
            total = await generic_command.count_by_category(db, category_id=category_id)
        else:
            # Get all commands
            commands = await generic_command.get_multi(db, skip=skip, limit=limit)
            total = len(commands)  # This is a simplified count

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        current_page = (skip // limit) + 1

        return GenericCommandListResponse(
            items=commands,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error getting commands: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving commands")


@router.post("/", response_model=GenericCommandResponse)
async def create_command(
    *,
    db: AsyncSession = Depends(get_db),
    command_in: GenericCommandCreate
):
    """
    Create a new generic command.

    **Request Body:**
    - template: Command template with parameter placeholders (required)
    - category_id: ID of the command category (required)
    - description: Optional description of the command
    - required_parameter_ids: List of required parameter IDs (optional)
    - created_by: Creator username (required)

    **Validation:**
    - Template must not be empty
    - Template parameter placeholders must be valid (alphanumeric + underscore)
    - Category must exist and be active
    - Required parameters must exist and be active

    **Example Request:**
    ```json
    {
        "template": "Set level of authentication {Authentication}",
        "category_id": "550e8400-e29b-41d4-a716-446655440000",
        "description": "Sets the authentication level for the ECU",
        "required_parameter_ids": ["550e8400-e29b-41d4-a716-446655440001"],
        "created_by": "admin"
    }
    ```

    **Example Response:**
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "template": "Set level of authentication {Authentication}",
        "category_id": "550e8400-e29b-41d4-a716-446655440000",
        "description": "Sets the authentication level for the ECU",
        "required_parameters": ["Authentication"],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "created_by": "admin",
        "is_active": true,
        "category": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "UDS Commands",
            "description": "UDS diagnostic commands"
        }
    }
    ```
    """
    try:
        # Create command with validation
        command = await generic_command.create_with_validation(db, obj_in=command_in)

        # Get the created command with relationships for response
        command_with_relations = await generic_command.get_with_all_relationships(db, id=str(command.id))

        return command_with_relations

    except ValidationError as e:
        logger.warning(f"Validation error creating command: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating command: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while creating command")


@router.get("/{command_id}", response_model=GenericCommandResponse)
async def get_command(
    *,
    db: AsyncSession = Depends(get_db),
    command_id: str = Path(..., description="Command ID"),
    include_category: bool = Query(True, description="Include category information"),
    include_parameters: bool = Query(True, description="Include required parameters")
):
    """
    Get a specific generic command by ID.

    **Path Parameters:**
    - command_id: The UUID of the command to retrieve

    **Query Parameters:**
    - include_category: Include category information in response (default: true)
    - include_parameters: Include required parameters in response (default: true)

    **Response:**
    Returns the command with all requested relationships loaded.

    **Example Request:**
    GET /commands/550e8400-e29b-41d4-a716-446655440000?include_parameters=true
    """
    try:
        if include_category and include_parameters:
            command = await generic_command.get_with_all_relationships(db, id=command_id)
        elif include_category:
            command = await generic_command.get_with_category(db, id=command_id)
        elif include_parameters:
            command = await generic_command.get_with_required_parameters(db, id=command_id)
        else:
            command = await generic_command.get(db, id=command_id)

        if not command:
            raise HTTPException(status_code=404, detail="Command not found")

        return command

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting command {command_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving command")


@router.put("/{command_id}", response_model=GenericCommandResponse)
async def update_command(
    *,
    db: AsyncSession = Depends(get_db),
    command_id: str = Path(..., description="Command ID"),
    command_in: GenericCommandUpdate
):
    """
    Update an existing generic command.

    **Path Parameters:**
    - command_id: The UUID of the command to update

    **Request Body:**
    All fields are optional for partial updates:
    - template: Updated command template
    - category_id: Updated category ID
    - description: Updated description
    - required_parameter_ids: Updated list of required parameter IDs

    **Validation:**
    - If template is updated, it must be valid
    - If category_id is updated, the category must exist and be active
    - If required_parameter_ids is updated, all parameters must exist and be active

    **Example Request:**
    ```json
    {
        "template": "Updated: Set level of authentication {Authentication}",
        "description": "Updated description of the command"
    }
    ```
    """
    try:
        # Get existing command
        command = await generic_command.get(db, id=command_id)
        if not command:
            raise HTTPException(status_code=404, detail="Command not found")

        # Update command with validation
        updated_command = await generic_command.update_with_validation(
            db, db_obj=command, obj_in=command_in
        )

        # Get the updated command with relationships for response
        command_with_relations = await generic_command.get_with_all_relationships(db, id=str(updated_command.id))

        return command_with_relations

    except HTTPException:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error updating command {command_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating command {command_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while updating command")


@router.delete("/{command_id}")
async def delete_command(
    *,
    db: AsyncSession = Depends(get_db),
    command_id: str = Path(..., description="Command ID")
):
    """
    Delete a generic command.

    **Path Parameters:**
    - command_id: The UUID of the command to delete

    **Validation:**
    - Command must exist
    - Command must not be in use by any test steps

    **Response:**
    Returns a success message upon successful deletion.

    **Error Responses:**
    - 404: Command not found
    - 409: Command is in use by test steps (conflict)
    - 500: Internal server error

    **Example Request:**
    DELETE /commands/550e8400-e29b-41d4-a716-446655440000
    """
    try:
        # Delete the command with validation
        await generic_command.remove_with_validation(db, id=command_id)

        return {"message": "Command deleted successfully"}

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting command {command_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while deleting command")


# Command Category Management Endpoints

@router.get("/categories/", response_model=List[CommandCategoryResponse])
async def get_command_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search categories by name"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    include_commands_count: bool = Query(True, description="Include commands count in response")
):
    """
    Get all command categories with filtering and pagination.

    **Filtering Options:**
    - search: Search by category name (case-insensitive partial match)
    - is_active: Filter by active status (default: true)
    - created_by: Filter by creator username

    **Response Options:**
    - include_commands_count: Include number of commands in each category (default: true)

    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)

    **Example Requests:**
    - Get all categories: GET /commands/categories/
    - Search categories: GET /commands/categories/?search=UDS
    - Filter by creator: GET /commands/categories/?created_by=admin
    """
    try:
        # Build filters
        filters = []

        if is_active is not None:
            filters.append(FilterCondition("is_active", FilterOperator.EQ, is_active))

        if created_by:
            filters.append(FilterCondition("created_by", FilterOperator.EQ, created_by))

        # Build search parameters
        search_params = None
        if search:
            search_params = SearchParams(
                search_term=search,
                search_fields=["name", "description"]
            )

        # Get categories
        categories = await command_category.get_multi_with_filters(
            db,
            filters=filters,
            search_params=search_params,
            skip=skip,
            limit=limit
        )

        # Add commands count if requested
        if include_commands_count:
            for category in categories:
                category.commands_count = await generic_command.count_by_category(
                    db, category_id=str(category.id)
                )

        return categories

    except Exception as e:
        logger.error(f"Error getting command categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving command categories")


@router.post("/categories/", response_model=CommandCategoryResponse)
async def create_command_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: CommandCategoryCreate
):
    """
    Create a new command category.

    **Request Body:**
    - name: Category name (required)
    - description: Optional description of the category
    - created_by: Creator username (required)

    **Validation:**
    - Name must be unique and not empty
    - Name must be between 1 and 255 characters

    **Example Request:**
    ```json
    {
        "name": "UDS",
        "description": "UDS diagnostic commands for automotive ECUs",
        "created_by": "admin"
    }
    ```
    """
    try:
        # Check if category with same name already exists
        existing_category = await command_category.get_by_name(db, name=category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=409,
                detail=f"Command category with name '{category_in.name}' already exists"
            )

        # Create category
        category = await command_category.create(db, obj_in=category_in)

        # Add commands count
        category.commands_count = 0

        return category

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating command category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while creating command category")


@router.get("/categories/{category_id}", response_model=CommandCategoryResponse)
async def get_command_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: str = Path(..., description="Category ID"),
    include_commands_count: bool = Query(True, description="Include commands count")
):
    """
    Get a specific command category by ID.

    **Path Parameters:**
    - category_id: The UUID of the category to retrieve

    **Query Parameters:**
    - include_commands_count: Include number of commands in category (default: true)

    **Example Request:**
    GET /commands/categories/550e8400-e29b-41d4-a716-446655440000
    """
    try:
        category = await command_category.get(db, id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Command category not found")

        # Add commands count if requested
        if include_commands_count:
            category.commands_count = await generic_command.count_by_category(
                db, category_id=category_id
            )

        return category

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting command category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving command category")


@router.put("/categories/{category_id}", response_model=CommandCategoryResponse)
async def update_command_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: str = Path(..., description="Category ID"),
    category_in: CommandCategoryUpdate
):
    """
    Update an existing command category.

    **Path Parameters:**
    - category_id: The UUID of the category to update

    **Request Body:**
    All fields are optional for partial updates:
    - name: Updated category name
    - description: Updated description

    **Validation:**
    - If name is updated, it must be unique and not empty
    - Name must be between 1 and 255 characters

    **Example Request:**
    ```json
    {
        "name": "Updated UDS",
        "description": "Updated description of UDS commands"
    }
    ```
    """
    try:
        # Get existing category
        category = await command_category.get(db, id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Command category not found")

        # Check for name conflicts if name is being updated
        if category_in.name and category_in.name != category.name:
            existing_category = await command_category.get_by_name(db, name=category_in.name)
            if existing_category:
                raise HTTPException(
                    status_code=409,
                    detail=f"Command category with name '{category_in.name}' already exists"
                )

        # Update category
        updated_category = await command_category.update(db, db_obj=category, obj_in=category_in)

        # Add commands count
        updated_category.commands_count = await generic_command.count_by_category(
            db, category_id=category_id
        )

        return updated_category

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating command category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while updating command category")


@router.delete("/categories/{category_id}")
async def delete_command_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: str = Path(..., description="Category ID")
):
    """
    Delete a command category.

    **Path Parameters:**
    - category_id: The UUID of the category to delete

    **Validation:**
    - Category must exist
    - Category must not have any commands assigned to it

    **Response:**
    Returns a success message upon successful deletion.

    **Example Request:**
    DELETE /commands/categories/550e8400-e29b-41d4-a716-446655440000
    """
    try:
        # Delete the category with validation
        await command_category.remove_with_validation(db, id=category_id)

        return {"message": "Command category deleted successfully"}

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting command category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while deleting command category")


# Advanced Search Endpoint

@router.get("/search/", response_model=GenericCommandListResponse)
async def search_commands(
    db: AsyncSession = Depends(get_db),
    q: str = Query(..., description="Search query"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    has_parameters: Optional[bool] = Query(None, description="Filter by commands with/without parameters"),
    min_parameters: Optional[int] = Query(None, ge=0, description="Minimum number of parameters"),
    max_parameters: Optional[int] = Query(None, ge=0, description="Maximum number of parameters"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order")
):
    """
    Advanced search for generic commands with multiple filtering options.

    **Search Parameters:**
    - q: Search query (searches in template and description)
    - category_id: Filter by command category ID
    - has_parameters: Filter by commands with/without parameters
    - min_parameters: Minimum number of parameters in command
    - max_parameters: Maximum number of parameters in command

    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)

    **Sorting:**
    - sort_by: Sort by field (template, created_at, updated_at) - default: created_at
    - sort_order: Sort order (asc, desc) - default: desc

    **Example Requests:**
    - Search by template: GET /commands/search/?q=authentication
    - Filter by category: GET /commands/search/?q=UDS&category_id=123
    - Filter by parameters: GET /commands/search/?q=diagnostic&has_parameters=true
    - Parameter count range: GET /commands/search/?q=test&min_parameters=1&max_parameters=3

    **Example Response:**
    ```json
    {
        "items": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "template": "Set level of authentication {Authentication}",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "description": "Sets the authentication level for the ECU",
                "required_parameters": ["Authentication"],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "created_by": "admin",
                "is_active": true
            }
        ],
        "total": 1,
        "page": 1,
        "per_page": 100,
        "total_pages": 1
    }
    ```
    """
    try:
        # Start with search by template
        commands = await generic_command.search_by_template(
            db, template=q, skip=0, limit=1000  # Get more for filtering
        )

        # Apply additional filters
        filtered_commands = []

        for command in commands:
            # Filter by category
            if category_id and str(command.category_id) != category_id:
                continue

            # Filter by parameter presence
            if has_parameters is not None:
                has_params = '{' in command.template
                if has_parameters != has_params:
                    continue

            # Filter by parameter count
            if min_parameters is not None or max_parameters is not None:
                param_count = generic_command._count_template_parameters(command.template)
                if min_parameters is not None and param_count < min_parameters:
                    continue
                if max_parameters is not None and param_count > max_parameters:
                    continue

            filtered_commands.append(command)

        # Apply sorting
        if sort_by == "template":
            filtered_commands.sort(key=lambda x: x.template, reverse=(sort_order == "desc"))
        elif sort_by == "created_at":
            filtered_commands.sort(key=lambda x: x.created_at, reverse=(sort_order == "desc"))
        elif sort_by == "updated_at":
            filtered_commands.sort(key=lambda x: x.updated_at, reverse=(sort_order == "desc"))

        # Apply pagination
        total = len(filtered_commands)
        paginated_commands = filtered_commands[skip:skip + limit]

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        current_page = (skip // limit) + 1

        return GenericCommandListResponse(
            items=paginated_commands,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error searching commands: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while searching commands")
