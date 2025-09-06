"""
API endpoints for Test Specifications management.

This module provides RESTful API endpoints for managing test specifications,
including CRUD operations, test steps management, and filtering functionality.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.crud.test_spec import test_specification, test_step
from app.schemas.test_spec import (
    TestSpecificationCreate,
    TestSpecificationUpdate,
    TestSpecificationResponse,
    TestSpecificationListResponse,
    TestStepCreate,
    TestStepUpdate,
    TestStepResponse,
    FunctionalArea
)
from app.utils.exceptions import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=TestSpecificationListResponse)
async def get_test_specifications(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    functional_area: Optional[FunctionalArea] = Query(None, description="Filter by functional area"),
    search: Optional[str] = Query(None, description="Search in name and description")
):
    """
    Get all test specifications with optional filtering and pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **functional_area**: Filter by functional area (UDS, Communication, ErrorHandler, CyberSecurity)
    - **search**: Search term for name and description (case-insensitive)
    """
    try:
        # Get test specifications with relationships loaded
        test_specs = await test_specification.get_multi_with_relationships(
            db, skip=skip, limit=limit, functional_area=functional_area, search=search
        )

        # Get total count for pagination
        total = await test_specification.count(db)

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        current_page = (skip // limit) + 1

        # Add computed fields to each test specification
        result_items = []
        for spec in test_specs:
            # Get requirements count
            requirements_count = len(spec.requirements) if spec.requirements else 0

            # Get test steps count
            test_steps_count = len(spec.test_steps) if spec.test_steps else 0

            # Create response object with only the fields we need
            result_items.append(TestSpecificationResponse(
                id=spec.id,
                name=spec.name,
                description=spec.description,
                precondition=spec.precondition,
                postcondition=spec.postcondition,
                test_data_description=spec.test_data_description,
                functional_area=spec.functional_area,
                created_at=spec.created_at,
                updated_at=spec.updated_at,
                created_by=spec.created_by,
                is_active=spec.is_active,
                requirements_count=requirements_count,
                test_steps_count=test_steps_count,
                requirement_ids=[str(req.id) for req in spec.requirements] if spec.requirements else []
            ))

        return TestSpecificationListResponse(
            items=result_items,
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error getting test specifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test specifications"
        )


@router.post("/", response_model=TestSpecificationResponse, status_code=status.HTTP_201_CREATED)
async def create_test_specification(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_in: TestSpecificationCreate
):
    """
    Create a new test specification.

    - **name**: Name of the test specification (required)
    - **description**: Detailed description of the test specification (required)
    - **precondition**: Precondition for executing the test (optional)
    - **postcondition**: Postcondition after executing the test (optional)
    - **test_data_description**: Description of test data and parameter variants (optional)
    - **functional_area**: Functional area this test specification belongs to (required)
    - **requirement_ids**: List of requirement IDs this test specification addresses (optional)
    - **created_by**: User creating the test specification (required)
    """
    try:
        # Create the test specification
        test_spec_obj = await test_specification.create(db, obj_in=test_spec_in)

        # Add requirements if provided
        if test_spec_in.requirement_ids:
            for req_id in test_spec_in.requirement_ids:
                try:
                    await test_specification.add_requirement(
                        db, test_spec_id=str(test_spec_obj.id), requirement_id=str(req_id)
                    )
                except NotFoundError as e:
                    logger.warning(f"Requirement {req_id} not found when creating test spec {test_spec_obj.id}: {str(e)}")
                    # Continue with other requirements

        # Get the complete test specification with relationships
        complete_test_spec = await test_specification.get_with_all_relationships(db, id=str(test_spec_obj.id))

        # Create response object
        spec_dict = complete_test_spec.__dict__.copy()
        spec_dict['requirements_count'] = len(complete_test_spec.requirements) if complete_test_spec.requirements else 0
        spec_dict['test_steps_count'] = len(complete_test_spec.test_steps) if complete_test_spec.test_steps else 0
        spec_dict['requirement_ids'] = [str(req.id) for req in complete_test_spec.requirements] if complete_test_spec.requirements else []

        return TestSpecificationResponse(**spec_dict)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating test specification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test specification"
        )


@router.get("/{test_spec_id}", response_model=TestSpecificationResponse)
async def get_test_specification(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_id: UUID = Path(..., description="Test specification ID"),
    include_steps: bool = Query(False, description="Include test steps in response")
):
    """
    Get a specific test specification by ID.

    - **test_spec_id**: UUID of the test specification to retrieve
    - **include_steps**: Whether to include test steps in the response
    """
    try:
        if include_steps:
            test_spec_obj = await test_specification.get_with_all_relationships(db, id=str(test_spec_id))
        else:
            test_spec_obj = await test_specification.get_with_requirements(db, id=str(test_spec_id))

        if not test_spec_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test specification not found"
            )

        # Create response object
        spec_dict = test_spec_obj.__dict__.copy()
        spec_dict['requirements_count'] = len(test_spec_obj.requirements) if test_spec_obj.requirements else 0
        spec_dict['test_steps_count'] = len(test_spec_obj.test_steps) if test_spec_obj.test_steps else 0
        spec_dict['requirement_ids'] = [str(req.id) for req in test_spec_obj.requirements] if test_spec_obj.requirements else []

        # Include test steps if requested
        if include_steps and test_spec_obj.test_steps:
            spec_dict['test_steps'] = [
                TestStepResponse(**step.__dict__) for step in test_spec_obj.test_steps
            ]

        return TestSpecificationResponse(**spec_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting test specification {test_spec_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test specification"
        )


@router.put("/{test_spec_id}", response_model=TestSpecificationResponse)
async def update_test_specification(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_id: UUID = Path(..., description="Test specification ID"),
    test_spec_in: TestSpecificationUpdate
):
    """
    Update an existing test specification.

    - **test_spec_id**: UUID of the test specification to update
    - **name**: Updated name (optional)
    - **description**: Updated description (optional)
    - **precondition**: Updated precondition (optional)
    - **postcondition**: Updated postcondition (optional)
    - **test_data_description**: Updated test data description (optional)
    - **functional_area**: Updated functional area (optional)
    - **requirement_ids**: Updated list of requirement IDs (optional)
    """
    try:
        test_spec_obj = await test_specification.get(db, id=str(test_spec_id))
        if not test_spec_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test specification not found"
            )

        # Update the test specification
        updated_test_spec = await test_specification.update(db, db_obj=test_spec_obj, obj_in=test_spec_in)

        # Update requirements if provided
        if test_spec_in.requirement_ids is not None:
            # Get current requirements
            current_spec = await test_specification.get_with_requirements(db, id=str(test_spec_id))
            current_req_ids = {str(req.id) for req in current_spec.requirements} if current_spec.requirements else set()
            new_req_ids = {str(req_id) for req_id in test_spec_in.requirement_ids}

            # Remove requirements that are no longer in the list
            for req_id in current_req_ids - new_req_ids:
                try:
                    await test_specification.remove_requirement(
                        db, test_spec_id=str(test_spec_id), requirement_id=req_id
                    )
                except NotFoundError:
                    pass  # Already removed or doesn't exist

            # Add new requirements
            for req_id in new_req_ids - current_req_ids:
                try:
                    await test_specification.add_requirement(
                        db, test_spec_id=str(test_spec_id), requirement_id=req_id
                    )
                except NotFoundError as e:
                    logger.warning(f"Requirement {req_id} not found when updating test spec {test_spec_id}: {str(e)}")

        # Get the complete updated test specification
        complete_test_spec = await test_specification.get_with_all_relationships(db, id=str(test_spec_id))

        # Create response object
        spec_dict = complete_test_spec.__dict__.copy()
        spec_dict['requirements_count'] = len(complete_test_spec.requirements) if complete_test_spec.requirements else 0
        spec_dict['test_steps_count'] = len(complete_test_spec.test_steps) if complete_test_spec.test_steps else 0
        spec_dict['requirement_ids'] = [str(req.id) for req in complete_test_spec.requirements] if complete_test_spec.requirements else []

        return TestSpecificationResponse(**spec_dict)

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating test specification {test_spec_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test specification"
        )


@router.delete("/{test_spec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_specification(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_id: UUID = Path(..., description="Test specification ID")
):
    """
    Delete a test specification.

    - **test_spec_id**: UUID of the test specification to delete
    """
    try:
        test_spec_obj = await test_specification.get(db, id=str(test_spec_id))
        if not test_spec_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test specification not found"
            )

        await test_specification.remove(db, id=str(test_spec_id))
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting test specification {test_spec_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test specification"
        )


@router.get("/{test_spec_id}/steps", response_model=List[TestStepResponse])
async def get_test_steps(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_id: UUID = Path(..., description="Test specification ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """
    Get all test steps for a specific test specification.

    - **test_spec_id**: UUID of the test specification
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    """
    try:
        # Verify test specification exists
        test_spec_obj = await test_specification.get(db, id=str(test_spec_id))
        if not test_spec_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test specification not found"
            )

        # Get test steps
        test_steps = await test_step.get_by_test_specification(
            db, test_specification_id=str(test_spec_id), skip=skip, limit=limit
        )

        return [TestStepResponse(**step.__dict__) for step in test_steps]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting test steps for test specification {test_spec_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test steps"
        )


@router.post("/{test_spec_id}/steps", response_model=TestStepResponse, status_code=status.HTTP_201_CREATED)
async def create_test_step(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_id: UUID = Path(..., description="Test specification ID"),
    test_step_in: TestStepCreate
):
    """
    Create a new test step for a test specification.

    - **test_spec_id**: UUID of the test specification
    - **action**: Action to be performed in this test step (required)
    - **expected_result**: Expected result for this test step (required)
    - **description**: Optional description of the test step
    - **sequence_number**: Sequence number of the test step (optional, auto-generated if not provided)
    - **created_by**: User creating the test step (required)
    """
    try:
        # Verify test specification exists
        test_spec_obj = await test_specification.get(db, id=str(test_spec_id))
        if not test_spec_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test specification not found"
            )

        # Set test specification ID and sequence number if not provided
        test_step_data = test_step_in.model_dump()
        test_step_data['test_specification_id'] = str(test_spec_id)

        if not test_step_data.get('sequence_number'):
            test_step_data['sequence_number'] = await test_step.get_next_sequence_number(
                db, test_specification_id=str(test_spec_id)
            )

        # Create the test step
        test_step_obj = await test_step.create(db, obj_in=TestStepCreate(**test_step_data))

        return TestStepResponse(**test_step_obj.__dict__)

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating test step for test specification {test_spec_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test step"
        )


@router.put("/{test_spec_id}/steps/{step_id}", response_model=TestStepResponse)
async def update_test_step(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_id: UUID = Path(..., description="Test specification ID"),
    step_id: UUID = Path(..., description="Test step ID"),
    test_step_in: TestStepUpdate
):
    """
    Update an existing test step.

    - **test_spec_id**: UUID of the test specification
    - **step_id**: UUID of the test step to update
    - **action**: Updated action (optional)
    - **expected_result**: Updated expected result (optional)
    - **description**: Updated description (optional)
    - **sequence_number**: Updated sequence number (optional)
    """
    try:
        # Verify test specification exists
        test_spec_obj = await test_specification.get(db, id=str(test_spec_id))
        if not test_spec_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test specification not found"
            )

        # Get the test step
        test_step_obj = await test_step.get(db, id=str(step_id))
        if not test_step_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test step not found"
            )

        # Verify the test step belongs to the test specification
        if str(test_step_obj.test_specification_id) != str(test_spec_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test step does not belong to the specified test specification"
            )

        # Update the test step
        updated_test_step = await test_step.update(db, db_obj=test_step_obj, obj_in=test_step_in)

        return TestStepResponse(**updated_test_step.__dict__)

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating test step {step_id} for test specification {test_spec_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test step"
        )


@router.delete("/{test_spec_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_step(
    *,
    db: AsyncSession = Depends(get_db),
    test_spec_id: UUID = Path(..., description="Test specification ID"),
    step_id: UUID = Path(..., description="Test step ID")
):
    """
    Delete a test step.

    - **test_spec_id**: UUID of the test specification
    - **step_id**: UUID of the test step to delete
    """
    try:
        # Verify test specification exists
        test_spec_obj = await test_specification.get(db, id=str(test_spec_id))
        if not test_spec_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test specification not found"
            )

        # Get the test step
        test_step_obj = await test_step.get(db, id=str(step_id))
        if not test_step_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test step not found"
            )

        # Verify the test step belongs to the test specification
        if str(test_step_obj.test_specification_id) != str(test_spec_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test step does not belong to the specified test specification"
            )

        # Delete the test step
        await test_step.remove(db, id=str(step_id))

        # Reorder sequence numbers for remaining steps
        await test_step.reorder_sequence_numbers(db, test_specification_id=str(test_spec_id))

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting test step {step_id} for test specification {test_spec_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test step"
        )
