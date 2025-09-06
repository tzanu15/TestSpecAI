"""
API endpoints for Parameter and ParameterVariant management.

This module provides RESTful endpoints for managing parameters, parameter categories,
and parameter variants with proper validation, error handling, and documentation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud.parameter import parameter, parameter_variant
from app.crud.category import parameter_category
from app.schemas.parameter import (
    ParameterCreate,
    ParameterUpdate,
    ParameterResponse,
    ParameterListResponse,
    ParameterCategoryCreate,
    ParameterCategoryUpdate,
    ParameterCategoryResponse,
    ParameterVariantCreate,
    ParameterVariantUpdate,
    ParameterVariantResponse
)
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
from app.crud.transaction_manager import transaction_context, execute_in_transaction
from app.crud.advanced_queries import FilterCondition, FilterOperator, SortCondition, SortDirection, PaginationParams, SearchParams
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Parameter Management Endpoints

@router.get("/", response_model=ParameterListResponse)
async def get_parameters(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category_id: Optional[str] = Query(None, description="Filter by parameter category ID"),
    has_variants: Optional[bool] = Query(None, description="Filter by parameters with/without variants"),
    search: Optional[str] = Query(None, description="Search parameters by name"),
    sort_by: str = Query("name", description="Sort by field (name, created_at, updated_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    include_variants: bool = Query(False, description="Include parameter variants in response"),
    include_category: bool = Query(True, description="Include category information in response")
):
    """
    Get all parameters with advanced filtering, sorting, and pagination.

    **Filtering Options:**
    - category_id: Filter by parameter category ID
    - has_variants: Filter by parameters with/without variants (true/false)
    - search: Search by parameter name (case-insensitive partial match)
    - is_active: Filter by active status (default: true)
    - created_by: Filter by creator username

    **Sorting Options:**
    - sort_by: Sort by field (name, created_at, updated_at) - default: name
    - sort_order: Sort order (asc, desc) - default: asc

    **Response Options:**
    - include_variants: Include parameter variants in response (default: false)
    - include_category: Include category information in response (default: true)

    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)

    **Example Requests:**
    - Get all parameters: GET /parameters/
    - Search parameters: GET /parameters/?search=authentication
    - Filter by category: GET /parameters/?category_id=123&has_variants=true
    - Sort by date: GET /parameters/?sort_by=created_at&sort_order=desc
    - Include variants: GET /parameters/?include_variants=true
    """
    try:
        # Build advanced filters
        filters = []

        if category_id:
            filters.append(FilterCondition("category_id", FilterOperator.EQ, category_id))

        if has_variants is not None:
            filters.append(FilterCondition("has_variants", FilterOperator.EQ, has_variants))

        if is_active is not None:
            filters.append(FilterCondition("is_active", FilterOperator.EQ, is_active))

        if created_by:
            filters.append(FilterCondition("created_by", FilterOperator.EQ, created_by))

        # Build sort conditions
        sorts = []
        if sort_by in ["name", "created_at", "updated_at"]:
            sort_direction = SortDirection.DESC if sort_order.lower() == "desc" else SortDirection.ASC
            sorts.append(SortCondition(sort_by, sort_direction))

        # Build pagination
        page = 1 + (skip // limit) if limit > 0 else 1
        pagination = PaginationParams(page=page, page_size=limit)

        # Build search parameters
        search_params = None
        if search:
            search_params = SearchParams(fields=["name", "description"], query=search)

        # Build relationships to include
        relationships = []
        if include_category:
            relationships.append("category")
        # Note: variants will be loaded separately to avoid greenlet issues

        # Get parameters with advanced filtering
        parameters_list = await parameter.get_with_filters(
            db,
            filters=filters,
            sorts=sorts,
            pagination=pagination,
            search=search_params,
            relationships=relationships if relationships else None
        )

        # Get total count with same filters
        total = await parameter.count_with_filters(
            db,
            filters=filters,
            search=search_params
        )

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit
        current_page = (skip // limit) + 1

        # Convert to response format, handling variants properly
        response_items = []
        for param in parameters_list:
            # Load variants separately if requested
            variants_data = None
            variants_count = 0
            if include_variants:
                variants = await parameter_variant.get_by_parameter(db, parameter_id=str(param.id))
                variants_data = [variant.__dict__ for variant in variants] if variants else []
                variants_count = len(variants) if variants else 0

            # Create a dict representation to avoid greenlet issues
            param_dict = {
                "id": str(param.id),
                "name": param.name,
                "category_id": str(param.category_id),
                "has_variants": param.has_variants,
                "default_value": param.default_value,
                "description": param.description,
                "created_at": param.created_at,
                "updated_at": param.updated_at,
                "created_by": param.created_by,
                "is_active": param.is_active,
                "category_name": param.category.name if param.category else None,
                "variants_count": variants_count,
                "variants": variants_data
            }
            response_items.append(param_dict)

        return ParameterListResponse(
            items=response_items,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error getting parameters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=ParameterResponse)
async def create_parameter(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_in: ParameterCreate
):
    """
    Create a new parameter with transaction management.

    **Validation Rules:**
    - Parameter name must be unique within the category
    - Category must exist and be active
    - Parameters with variants cannot have default values
    - Parameters without variants must have default values

    **Request Body Example:**
    ```json
    {
        "name": "Authentication Level",
        "description": "Level of authentication required for UDS access",
        "category_id": "123e4567-e89b-12d3-a456-426614174000",
        "has_variants": true,
        "variants": [
            {
                "manufacturer": "BMW",
                "value": "Level 1",
                "description": "Basic authentication for BMW vehicles"
            },
            {
                "manufacturer": "VW",
                "value": "Level 2",
                "description": "Enhanced authentication for VW vehicles"
            }
        ]
    }
    ```

    **Response Example:**
    ```json
    {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "name": "Authentication Level",
        "description": "Level of authentication required for UDS access",
        "category_id": "123e4567-e89b-12d3-a456-426614174000",
        "has_variants": true,
        "default_value": null,
        "variants": [...],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "created_by": "admin",
        "is_active": true
    }
    ```
    """
    try:
        parameter_obj = await parameter.create_with_validation(db, obj_in=parameter_in)

        # Convert to dict to avoid lazy loading issues during serialization
        parameter_dict = {
            "id": str(parameter_obj.id),
            "name": parameter_obj.name,
            "description": parameter_obj.description,
            "category_id": str(parameter_obj.category_id),
            "has_variants": parameter_obj.has_variants,
            "default_value": parameter_obj.default_value,
            "created_at": parameter_obj.created_at,
            "updated_at": parameter_obj.updated_at,
            "created_by": parameter_obj.created_by,
            "is_active": parameter_obj.is_active,
            "variants": []  # Empty variants for new parameters
        }

        return parameter_dict
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating parameter: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{parameter_id}", response_model=ParameterResponse)
async def get_parameter(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID"),
    include_variants: bool = Query(False, description="Include parameter variants"),
    include_category: bool = Query(True, description="Include category information")
):
    """
    Get a specific parameter by ID.

    Supports including:
    - variants: Include parameter variants in response
    - category: Include category information in response
    """
    try:
        if include_variants and include_category:
            parameter_obj = await parameter.get_with_all_relationships(db, id=parameter_id)
        elif include_variants:
            parameter_obj = await parameter.get_with_variants(db, id=parameter_id)
        elif include_category:
            parameter_obj = await parameter.get_with_category(db, id=parameter_id)
        else:
            parameter_obj = await parameter.get(db, id=parameter_id)

        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        # Convert to dict to avoid lazy loading issues during serialization
        parameter_dict = {
            "id": str(parameter_obj.id),
            "name": parameter_obj.name,
            "description": parameter_obj.description,
            "category_id": str(parameter_obj.category_id),
            "has_variants": parameter_obj.has_variants,
            "default_value": parameter_obj.default_value,
            "created_at": parameter_obj.created_at,
            "updated_at": parameter_obj.updated_at,
            "created_by": parameter_obj.created_by,
            "is_active": parameter_obj.is_active,
            "variants": []  # Will be populated separately if needed
        }

        # Load variants separately if requested
        if include_variants:
            variants = await parameter_variant.get_by_parameter(db, parameter_id=parameter_id)
            parameter_dict["variants"] = [
                {
                    "id": str(variant.id),
                    "manufacturer": variant.manufacturer,
                    "value": variant.value,
                    "description": variant.description,
                    "created_at": variant.created_at,
                    "updated_at": variant.updated_at,
                    "created_by": variant.created_by,
                    "is_active": variant.is_active
                }
                for variant in variants
            ]

        return parameter_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameter {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{parameter_id}", response_model=ParameterResponse)
async def update_parameter(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID"),
    parameter_in: ParameterUpdate
):
    """
    Update an existing parameter with transaction management.

    Validates that:
    - Parameter exists
    - New parameter name is unique (if changed)
    - Category exists and is active (if changed)
    - Parameters with variants don't have default values
    - Parameters without variants have default values
    """
    try:
        parameter_obj = await parameter.get(db, id=parameter_id)
        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        updated_parameter = await parameter.update_with_validation(
            db, db_obj=parameter_obj, obj_in=parameter_in
        )

        # Convert to dict to avoid lazy loading issues during serialization
        parameter_dict = {
            "id": str(updated_parameter.id),
            "name": updated_parameter.name,
            "description": updated_parameter.description,
            "category_id": str(updated_parameter.category_id),
            "has_variants": updated_parameter.has_variants,
            "default_value": updated_parameter.default_value,
            "created_at": updated_parameter.created_at,
            "updated_at": updated_parameter.updated_at,
            "created_by": updated_parameter.created_by,
            "is_active": updated_parameter.is_active,
            "variants": []  # Empty variants for updated parameters
        }

        return parameter_dict
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating parameter {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{parameter_id}")
async def delete_parameter(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID")
):
    """
    Delete a parameter with transaction management.

    Note: This performs a soft delete by setting is_active to False.
    The parameter and its variants will be marked as inactive but not physically removed.
    """
    try:
        parameter_obj = await parameter.get(db, id=parameter_id)
        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        # Soft delete the parameter
        await parameter.remove(db, id=parameter_id)
        return {"message": "Parameter deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting parameter {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Parameter Category Management Endpoints

@router.get("/categories/", response_model=List[ParameterCategoryResponse])
async def get_parameter_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search categories by name"),
    sort_by: str = Query("name", description="Sort by field (name, created_at, updated_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    created_by: Optional[str] = Query(None, description="Filter by creator")
):
    """
    Get all parameter categories with advanced filtering, sorting, and pagination.

    **Filtering Options:**
    - search: Search by category name (case-insensitive partial match)
    - is_active: Filter by active status (default: true)
    - created_by: Filter by creator username

    **Sorting Options:**
    - sort_by: Sort by field (name, created_at, updated_at) - default: name
    - sort_order: Sort order (asc, desc) - default: asc

    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)

    **Example Requests:**
    - Get all categories: GET /parameters/categories/
    - Search categories: GET /parameters/categories/?search=authentication
    - Sort by date: GET /parameters/categories/?sort_by=created_at&sort_order=desc
    - Filter by creator: GET /parameters/categories/?created_by=admin
    """
    try:
        # Build advanced filters
        filters = []

        if is_active is not None:
            filters.append(FilterCondition("is_active", FilterOperator.EQ, is_active))

        if created_by:
            filters.append(FilterCondition("created_by", FilterOperator.EQ, created_by))

        # Build sort conditions
        sorts = []
        if sort_by in ["name", "created_at", "updated_at"]:
            sort_direction = SortDirection.DESC if sort_order.lower() == "desc" else SortDirection.ASC
            sorts.append(SortCondition(sort_by, sort_direction))

        # Build pagination
        page = 1 + (skip // limit) if limit > 0 else 1
        pagination = PaginationParams(page=page, page_size=limit)

        # Build search parameters
        search_params = None
        if search:
            search_params = SearchParams(fields=["name", "description"], query=search)

        # Get categories with advanced filtering
        categories = await parameter_category.get_with_filters(
            db,
            filters=filters,
            sorts=sorts,
            pagination=pagination,
            search=search_params
        )

        return categories
    except Exception as e:
        logger.error(f"Error getting parameter categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/categories/", response_model=ParameterCategoryResponse)
async def create_parameter_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: ParameterCategoryCreate
):
    """
    Create a new parameter category with transaction management.

    **Validation Rules:**
    - Category name must be unique across all categories
    - Name cannot be empty or contain only whitespace

    **Request Body Example:**
    ```json
    {
        "name": "UDS Authentication",
        "description": "Parameters related to UDS authentication mechanisms"
    }
    ```

    **Response Example:**
    ```json
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "UDS Authentication",
        "description": "Parameters related to UDS authentication mechanisms",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "created_by": "admin",
        "is_active": true
    }
    ```
    """
    try:
        category_obj = await parameter_category.create_with_validation(db, obj_in=category_in)
        return category_obj
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating parameter category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/categories/{category_id}", response_model=ParameterCategoryResponse)
async def get_parameter_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: str = Path(..., description="Parameter category ID")
):
    """
    Get a specific parameter category by ID.
    """
    try:
        category_obj = await parameter_category.get(db, id=category_id)
        if not category_obj:
            raise HTTPException(status_code=404, detail="Parameter category not found")

        return category_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameter category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/categories/{category_id}", response_model=ParameterCategoryResponse)
async def update_parameter_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: str = Path(..., description="Parameter category ID"),
    category_in: ParameterCategoryUpdate
):
    """
    Update an existing parameter category.

    Validates that:
    - Category exists
    - New category name is unique (if changed)
    """
    try:
        category_obj = await parameter_category.get(db, id=category_id)
        if not category_obj:
            raise HTTPException(status_code=404, detail="Parameter category not found")

        updated_category = await parameter_category.update_with_validation(
            db, db_obj=category_obj, obj_in=category_in
        )
        return updated_category
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating parameter category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/categories/{category_id}")
async def delete_parameter_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: str = Path(..., description="Parameter category ID")
):
    """
    Delete a parameter category.

    Note: This performs a soft delete by setting is_active to False.
    The category will be marked as inactive but not physically removed.
    """
    try:
        category_obj = await parameter_category.get(db, id=category_id)
        if not category_obj:
            raise HTTPException(status_code=404, detail="Parameter category not found")

        # Soft delete the category
        await parameter_category.remove(db, id=category_id)

        return {"message": "Parameter category deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting parameter category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Parameter Variant Management Endpoints

@router.get("/{parameter_id}/variants/", response_model=List[ParameterVariantResponse])
async def get_parameter_variants(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    sort_by: str = Query("manufacturer", description="Sort by field (manufacturer, value, created_at, updated_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    created_by: Optional[str] = Query(None, description="Filter by creator")
):
    """
    Get all variants for a specific parameter with advanced filtering, sorting, and pagination.

    **Filtering Options:**
    - manufacturer: Filter by manufacturer name (exact match)
    - is_active: Filter by active status (default: true)
    - created_by: Filter by creator username

    **Sorting Options:**
    - sort_by: Sort by field (manufacturer, value, created_at, updated_at) - default: manufacturer
    - sort_order: Sort order (asc, desc) - default: asc

    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)

    **Example Requests:**
    - Get all variants: GET /parameters/{parameter_id}/variants/
    - Filter by manufacturer: GET /parameters/{parameter_id}/variants/?manufacturer=BMW
    - Sort by value: GET /parameters/{parameter_id}/variants/?sort_by=value&sort_order=desc
    - Filter by creator: GET /parameters/{parameter_id}/variants/?created_by=admin
    """
    try:
        # Verify parameter exists
        parameter_obj = await parameter.get(db, id=parameter_id)
        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        # Build advanced filters
        filters = []

        # Always filter by parameter_id
        filters.append(FilterCondition("parameter_id", FilterOperator.EQ, parameter_id))

        if manufacturer:
            filters.append(FilterCondition("manufacturer", FilterOperator.EQ, manufacturer))

        if is_active is not None:
            filters.append(FilterCondition("is_active", FilterOperator.EQ, is_active))

        if created_by:
            filters.append(FilterCondition("created_by", FilterOperator.EQ, created_by))

        # Build sort conditions
        sorts = []
        if sort_by in ["manufacturer", "value", "created_at", "updated_at"]:
            sort_direction = SortDirection.DESC if sort_order.lower() == "desc" else SortDirection.ASC
            sorts.append(SortCondition(sort_by, sort_direction))

        # Build pagination
        page = 1 + (skip // limit) if limit > 0 else 1
        pagination = PaginationParams(page=page, page_size=limit)

        # Get variants with advanced filtering
        variants = await parameter_variant.get_with_filters(
            db,
            filters=filters,
            sorts=sorts,
            pagination=pagination
        )

        return variants
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameter variants for {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{parameter_id}/variants/", response_model=ParameterVariantResponse)
async def create_parameter_variant(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID"),
    variant_in: ParameterVariantCreate
):
    """
    Create a new parameter variant with transaction management.

    **Validation Rules:**
    - Parameter must exist and be active
    - Variant for this parameter and manufacturer combination must be unique
    - Manufacturer name cannot be empty
    - Value cannot be empty

    **Request Body Example:**
    ```json
    {
        "manufacturer": "BMW",
        "value": "Level 1",
        "description": "Basic authentication for BMW vehicles"
    }
    ```

    **Response Example:**
    ```json
    {
        "id": "789e0123-e89b-12d3-a456-426614174002",
        "parameter_id": "456e7890-e89b-12d3-a456-426614174001",
        "manufacturer": "BMW",
        "value": "Level 1",
        "description": "Basic authentication for BMW vehicles",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "created_by": "admin",
        "is_active": true
    }
    ```
    """
    try:
        # Verify parameter exists
        parameter_obj = await parameter.get(db, id=parameter_id)
        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        # Set the parameter_id in the variant data
        variant_in.parameter_id = parameter_id

        variant_obj = await parameter_variant.create_with_validation(db, obj_in=variant_in)
        return variant_obj
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating parameter variant for {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{parameter_id}/variants/{variant_id}", response_model=ParameterVariantResponse)
async def get_parameter_variant(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID"),
    variant_id: str = Path(..., description="Parameter variant ID")
):
    """
    Get a specific parameter variant by ID.
    """
    try:
        # Verify parameter exists
        parameter_obj = await parameter.get(db, id=parameter_id)
        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        variant_obj = await parameter_variant.get(db, id=variant_id)
        if not variant_obj:
            raise HTTPException(status_code=404, detail="Parameter variant not found")

        # Verify variant belongs to the parameter
        if str(variant_obj.parameter_id) != parameter_id:
            raise HTTPException(status_code=404, detail="Parameter variant not found for this parameter")

        return variant_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameter variant {variant_id} for {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{parameter_id}/variants/{variant_id}", response_model=ParameterVariantResponse)
async def update_parameter_variant(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID"),
    variant_id: str = Path(..., description="Parameter variant ID"),
    variant_in: ParameterVariantUpdate
):
    """
    Update an existing parameter variant with transaction management.

    Validates that:
    - Parameter exists
    - Variant exists and belongs to the parameter
    - New manufacturer doesn't conflict with existing variant for the same parameter
    """
    try:
        # Verify parameter exists
        parameter_obj = await parameter.get(db, id=parameter_id)
        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        variant_obj = await parameter_variant.get(db, id=variant_id)
        if not variant_obj:
            raise HTTPException(status_code=404, detail="Parameter variant not found")

        # Verify variant belongs to the parameter
        if str(variant_obj.parameter_id) != parameter_id:
            raise HTTPException(status_code=404, detail="Parameter variant not found for this parameter")

        updated_variant = await parameter_variant.update_with_validation(
            db, db_obj=variant_obj, obj_in=variant_in
        )
        return updated_variant
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating parameter variant {variant_id} for {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{parameter_id}/variants/{variant_id}")
async def delete_parameter_variant(
    *,
    db: AsyncSession = Depends(get_db),
    parameter_id: str = Path(..., description="Parameter ID"),
    variant_id: str = Path(..., description="Parameter variant ID")
):
    """
    Delete a parameter variant with transaction management.

    Note: This performs a soft delete by setting is_active to False.
    The variant will be marked as inactive but not physically removed.
    """
    try:
        # Verify parameter exists
        parameter_obj = await parameter.get(db, id=parameter_id)
        if not parameter_obj:
            raise HTTPException(status_code=404, detail="Parameter not found")

        variant_obj = await parameter_variant.get(db, id=variant_id)
        if not variant_obj:
            raise HTTPException(status_code=404, detail="Parameter variant not found")

        # Verify variant belongs to the parameter
        if str(variant_obj.parameter_id) != parameter_id:
            raise HTTPException(status_code=404, detail="Parameter variant not found for this parameter")

        # Soft delete the variant
        await parameter_variant.remove(db, id=variant_id)
        return {"message": "Parameter variant deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting parameter variant {variant_id} for {parameter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
