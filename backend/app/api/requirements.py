"""
API endpoints for Requirements management.

This module provides RESTful API endpoints for managing requirements,
including CRUD operations, search functionality, and category management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.crud.requirement import requirement
from app.crud.category import requirement_category
from app.schemas.requirement import (
    RequirementCreate,
    RequirementUpdate,
    RequirementResponse,
    RequirementListResponse
)
from app.schemas.category import (
    RequirementCategoryCreate,
    RequirementCategoryUpdate,
    RequirementCategoryResponse
)
from app.utils.exceptions import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=RequirementListResponse)
async def get_requirements(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    source: Optional[str] = Query(None, description="Filter by source"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """
    Get all requirements with optional filtering and pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **category_id**: Filter by requirement category ID
    - **source**: Filter by requirement source (e.g., 'manual', 'document')
    - **search**: Search term for title and description (case-insensitive)
    """
    try:
        # Determine which query method to use based on filters
        if category_id:
            requirements = await requirement.get_by_category(
                db, category_id=str(category_id), skip=skip, limit=limit
            )
        elif source:
            requirements = await requirement.get_by_source(
                db, source=source, skip=skip, limit=limit
            )
        elif search:
            # For search, we'll search in both title and description
            title_results = await requirement.search_by_title(
                db, title=search, skip=0, limit=limit
            )
            desc_results = await requirement.search_by_description(
                db, description=search, skip=0, limit=limit
            )
            # Combine and deduplicate results
            seen_ids = set()
            requirements = []
            for req in title_results + desc_results:
                if str(req.id) not in seen_ids:
                    requirements.append(req)
                    seen_ids.add(str(req.id))
            # Apply pagination to combined results
            requirements = requirements[skip:skip + limit]
        else:
            requirements = await requirement.get_multi(db, skip=skip, limit=limit)

        # Get total count for pagination
        total = await requirement.count(db)

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        current_page = (skip // limit) + 1

        return RequirementListResponse(
            items=requirements,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error getting requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirements"
        )


@router.post("/", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    *,
    db: AsyncSession = Depends(get_db),
    requirement_in: RequirementCreate
):
    """
    Create a new requirement.

    - **title**: Title of the requirement (required)
    - **description**: Detailed description of the requirement (required)
    - **category_id**: ID of the requirement category (required)
    - **source**: Source of the requirement (default: "manual")
    - **metadata**: Additional metadata (optional)
    - **created_by**: User creating the requirement (required)
    """
    try:
        requirement_obj = await requirement.create_with_validation(db, obj_in=requirement_in)
        return requirement_obj
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating requirement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create requirement"
        )


@router.get("/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    *,
    db: AsyncSession = Depends(get_db),
    requirement_id: UUID = Path(..., description="Requirement ID")
):
    """
    Get a specific requirement by ID.

    - **requirement_id**: UUID of the requirement to retrieve
    """
    try:
        requirement_obj = await requirement.get_with_all_relationships(db, id=str(requirement_id))
        if not requirement_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        return requirement_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting requirement {requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirement"
        )


@router.put("/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    *,
    db: AsyncSession = Depends(get_db),
    requirement_id: UUID = Path(..., description="Requirement ID"),
    requirement_in: RequirementUpdate
):
    """
    Update an existing requirement.

    - **requirement_id**: UUID of the requirement to update
    - **title**: Updated title (optional)
    - **description**: Updated description (optional)
    - **category_id**: Updated category ID (optional)
    - **source**: Updated source (optional)
    - **metadata**: Updated metadata (optional)
    """
    try:
        requirement_obj = await requirement.get(db, id=str(requirement_id))
        if not requirement_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )

        # Validate category if being updated
        if requirement_in.category_id:
            if not await requirement.validate_category_exists(db, category_id=str(requirement_in.category_id)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with ID {requirement_in.category_id} does not exist"
                )

        updated_requirement = await requirement.update(db, db_obj=requirement_obj, obj_in=requirement_in)
        return updated_requirement

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating requirement {requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update requirement"
        )


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement(
    *,
    db: AsyncSession = Depends(get_db),
    requirement_id: UUID = Path(..., description="Requirement ID")
):
    """
    Delete a requirement.

    - **requirement_id**: UUID of the requirement to delete
    """
    try:
        requirement_obj = await requirement.get(db, id=str(requirement_id))
        if not requirement_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )

        await requirement.remove(db, id=str(requirement_id))
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting requirement {requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete requirement"
        )


@router.get("/categories/", response_model=List[RequirementCategoryResponse])
async def get_requirement_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in category name")
):
    """
    Get all requirement categories with optional filtering.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **search**: Search term for category name (case-insensitive)
    """
    try:
        if search:
            categories = await requirement_category.search_by_name(
                db, name=search, skip=skip, limit=limit
            )
        else:
            categories = await requirement_category.get_with_requirements_count(
                db, skip=skip, limit=limit
            )

        # Add requirements count to each category
        result = []
        for category in categories:
            count = await requirement.count_by_category(db, category_id=str(category.id))
            category_dict = category.__dict__.copy()
            category_dict['requirements_count'] = count
            result.append(RequirementCategoryResponse(**category_dict))

        return result

    except Exception as e:
        logger.error(f"Error getting requirement categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirement categories"
        )


@router.post("/categories/", response_model=RequirementCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: RequirementCategoryCreate
):
    """
    Create a new requirement category.

    - **name**: Name of the category (required, must be unique)
    - **description**: Description of the category (optional)
    - **created_by**: User creating the category (required)
    """
    try:
        category_obj = await requirement_category.create_with_validation(db, obj_in=category_in)
        return category_obj
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating requirement category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create requirement category"
        )


@router.get("/categories/{category_id}", response_model=RequirementCategoryResponse)
async def get_requirement_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: UUID = Path(..., description="Category ID")
):
    """
    Get a specific requirement category by ID.

    - **category_id**: UUID of the category to retrieve
    """
    try:
        category_obj = await requirement_category.get(db, id=str(category_id))
        if not category_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement category not found"
            )

        # Add requirements count
        count = await requirement.count_by_category(db, category_id=str(category_id))
        category_dict = category_obj.__dict__.copy()
        category_dict['requirements_count'] = count

        return RequirementCategoryResponse(**category_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting requirement category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirement category"
        )


@router.put("/categories/{category_id}", response_model=RequirementCategoryResponse)
async def update_requirement_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: UUID = Path(..., description="Category ID"),
    category_in: RequirementCategoryUpdate
):
    """
    Update an existing requirement category.

    - **category_id**: UUID of the category to update
    - **name**: Updated name (optional, must be unique)
    - **description**: Updated description (optional)
    """
    try:
        category_obj = await requirement_category.get(db, id=str(category_id))
        if not category_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement category not found"
            )

        updated_category = await requirement_category.update_with_validation(
            db, db_obj=category_obj, obj_in=category_in
        )

        # Add requirements count
        count = await requirement.count_by_category(db, category_id=str(category_id))
        category_dict = updated_category.__dict__.copy()
        category_dict['requirements_count'] = count

        return RequirementCategoryResponse(**category_dict)

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating requirement category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update requirement category"
        )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: UUID = Path(..., description="Category ID")
):
    """
    Delete a requirement category.

    - **category_id**: UUID of the category to delete
    """
    try:
        category_obj = await requirement_category.get(db, id=str(category_id))
        if not category_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement category not found"
            )

        # Check if category has requirements
        count = await requirement.count_by_category(db, category_id=str(category_id))
        if count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category with {count} requirements. Please reassign or delete requirements first."
            )

        await requirement_category.remove(db, id=str(category_id))
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting requirement category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete requirement category"
        )


@router.get("/search/", response_model=RequirementListResponse)
async def search_requirements(
    db: AsyncSession = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    source: Optional[str] = Query(None, description="Filter by source")
):
    """
    Advanced search for requirements with multiple criteria.

    - **q**: Search query (searches in title and description)
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **category_id**: Filter by requirement category ID
    - **source**: Filter by requirement source
    """
    try:
        # Start with search results
        title_results = await requirement.search_by_title(
            db, title=q, skip=0, limit=limit * 2  # Get more to account for filtering
        )
        desc_results = await requirement.search_by_description(
            db, description=q, skip=0, limit=limit * 2
        )

        # Combine and deduplicate results
        seen_ids = set()
        requirements = []
        for req in title_results + desc_results:
            if str(req.id) not in seen_ids:
                requirements.append(req)
                seen_ids.add(str(req.id))

        # Apply additional filters
        if category_id:
            requirements = [req for req in requirements if str(req.category_id) == str(category_id)]

        if source:
            requirements = [req for req in requirements if req.source == source]

        # Apply pagination to filtered results
        total = len(requirements)
        requirements = requirements[skip:skip + limit]

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        current_page = (skip // limit) + 1

        return RequirementListResponse(
            items=requirements,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error searching requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search requirements"
        )
