"""
API endpoint tests for TestSpecification and TestStep management.

This module tests all RESTful endpoints for test specifications and test steps
with comprehensive test coverage including CRUD operations, validation, and error handling.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.test_spec import TestSpecification, TestStep, FunctionalArea
from app.models.requirement import Requirement
from app.models.category import RequirementCategory
from app.models.command import GenericCommand
from app.models.category import CommandCategory
from app.schemas.test_spec import TestSpecificationCreate, TestStepCreate


@pytest.mark.asyncio
async def test_create_test_specification(client: AsyncClient, db_session: AsyncSession):
    """Test test specification creation via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    # Create test specification
    response = await client.post(
        "/api/v1/test-specifications/",
        json={
            "name": "Test Specification",
            "description": "Test specification description",
            "requirement_ids": [str(requirement.id)],
            "precondition": "System is initialized",
            "postcondition": "Test completed successfully",
            "test_data_description": {"param1": "value1"},
            "functional_area": "UDS",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Specification"
    assert data["functional_area"] == "UDS"
    assert len(data["requirement_ids"]) == 1
    assert data["requirement_ids"][0] == str(requirement.id)


@pytest.mark.asyncio
async def test_create_test_specification_with_steps(client: AsyncClient, db_session: AsyncSession):
    """Test test specification creation with test steps"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    cmd_category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(cmd_category)
    await db_session.commit()
    await db_session.refresh(cmd_category)

    command = GenericCommand(
        template="Test command {Parameter}",
        category_id=cmd_category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    # Create test specification with steps
    response = await client.post(
        "/api/v1/test-specifications/",
        json={
            "name": "Test Specification with Steps",
            "description": "Test specification with steps description",
            "requirement_ids": [str(requirement.id)],
            "precondition": "System is initialized",
            "postcondition": "Test completed successfully",
            "test_data_description": {"param1": "value1"},
            "functional_area": "UDS",
            "test_steps": [
                {
                    "action": {
                        "command_id": str(command.id),
                        "populated_parameters": {"Parameter": "value1"}
                    },
                    "expected_result": {
                        "command_id": str(command.id),
                        "populated_parameters": {"Parameter": "value1"}
                    },
                    "description": "Test step description",
                    "sequence_number": 1
                }
            ],
            "created_by": "test-user"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Specification with Steps"
    assert len(data["test_steps"]) == 1
    assert data["test_steps"][0]["sequence_number"] == 1


@pytest.mark.asyncio
async def test_get_test_specifications(client: AsyncClient, db_session: AsyncSession):
    """Test getting test specifications via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()

    # Get test specifications
    response = await client.get("/api/v1/test-specifications/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Specification"


@pytest.mark.asyncio
async def test_get_test_specifications_with_pagination(client: AsyncClient, db_session: AsyncSession):
    """Test getting test specifications with pagination"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    # Create multiple test specifications
    for i in range(5):
        test_spec = TestSpecification(
            name=f"Test Specification {i}",
            description=f"Test specification description {i}",
            precondition="System is initialized",
            postcondition="Test completed successfully",
            test_data_description={"param1": "value1"},
            functional_area=FunctionalArea.UDS,
            created_by="test-user"
        )
        db_session.add(test_spec)
    await db_session.commit()

    # Get test specifications with pagination
    response = await client.get("/api/v1/test-specifications/?skip=0&limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_get_test_specifications_by_functional_area(client: AsyncClient, db_session: AsyncSession):
    """Test getting test specifications filtered by functional area"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    # Create test specifications for different functional areas
    test_spec1 = TestSpecification(
        name="UDS Test Specification",
        description="UDS test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    test_spec2 = TestSpecification(
        name="Communication Test Specification",
        description="Communication test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.COMMUNICATION,
        created_by="test-user"
    )
    db_session.add(test_spec1)
    db_session.add(test_spec2)
    await db_session.commit()

    # Get test specifications by functional area
    response = await client.get("/api/v1/test-specifications/?functional_area=UDS")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "UDS Test Specification"


@pytest.mark.asyncio
async def test_get_test_specification_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific test specification by ID"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    # Get test specification by ID
    response = await client.get(f"/api/v1/test-specifications/{test_spec.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Specification"
    assert data["id"] == str(test_spec.id)


@pytest.mark.asyncio
async def test_get_test_specification_not_found(client: AsyncClient):
    """Test getting non-existent test specification"""
    response = await client.get("/api/v1/test-specifications/non-existent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_test_specification(client: AsyncClient, db_session: AsyncSession):
    """Test test specification update via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    # Update test specification
    response = await client.put(
        f"/api/v1/test-specifications/{test_spec.id}",
        json={
            "name": "Updated Test Specification",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Specification"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_test_specification_not_found(client: AsyncClient):
    """Test updating non-existent test specification"""
    response = await client.put(
        "/api/v1/test-specifications/non-existent-id",
        json={
            "name": "Updated Test Specification"
        }
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_test_specification(client: AsyncClient, db_session: AsyncSession):
    """Test test specification deletion via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    # Delete test specification
    response = await client.delete(f"/api/v1/test-specifications/{test_spec.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Test specification deleted successfully"

    # Verify deletion
    get_response = await client.get(f"/api/v1/test-specifications/{test_spec.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_test_specification_not_found(client: AsyncClient):
    """Test deleting non-existent test specification"""
    response = await client.delete("/api/v1/test-specifications/non-existent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_test_step(client: AsyncClient, db_session: AsyncSession):
    """Test test step creation via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    cmd_category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(cmd_category)
    await db_session.commit()
    await db_session.refresh(cmd_category)

    command = GenericCommand(
        template="Test command {Parameter}",
        category_id=cmd_category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    # Create test step
    response = await client.post(
        f"/api/v1/test-specifications/{test_spec.id}/steps",
        json={
            "action": {
                "command_id": str(command.id),
                "populated_parameters": {"Parameter": "value1"}
            },
            "expected_result": {
                "command_id": str(command.id),
                "populated_parameters": {"Parameter": "value1"}
            },
            "description": "Test step description",
            "sequence_number": 1,
            "created_by": "test-user"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test step description"
    assert data["sequence_number"] == 1


@pytest.mark.asyncio
async def test_get_test_steps(client: AsyncClient, db_session: AsyncSession):
    """Test getting test steps via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    cmd_category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(cmd_category)
    await db_session.commit()
    await db_session.refresh(cmd_category)

    command = GenericCommand(
        template="Test command {Parameter}",
        category_id=cmd_category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    test_step = TestStep(
        test_specification_id=test_spec.id,
        action={
            "command_id": str(command.id),
            "populated_parameters": {"Parameter": "value1"}
        },
        expected_result={
            "command_id": str(command.id),
            "populated_parameters": {"Parameter": "value1"}
        },
        description="Test step description",
        sequence_number=1,
        created_by="test-user"
    )
    db_session.add(test_step)
    await db_session.commit()

    # Get test steps
    response = await client.get(f"/api/v1/test-specifications/{test_spec.id}/steps")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["description"] == "Test step description"


@pytest.mark.asyncio
async def test_update_test_step(client: AsyncClient, db_session: AsyncSession):
    """Test test step update via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    cmd_category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(cmd_category)
    await db_session.commit()
    await db_session.refresh(cmd_category)

    command = GenericCommand(
        template="Test command {Parameter}",
        category_id=cmd_category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    test_step = TestStep(
        test_specification_id=test_spec.id,
        action={
            "command_id": str(command.id),
            "populated_parameters": {"Parameter": "value1"}
        },
        expected_result={
            "command_id": str(command.id),
            "populated_parameters": {"Parameter": "value1"}
        },
        description="Test step description",
        sequence_number=1,
        created_by="test-user"
    )
    db_session.add(test_step)
    await db_session.commit()
    await db_session.refresh(test_step)

    # Update test step
    response = await client.put(
        f"/api/v1/test-specifications/{test_spec.id}/steps/{test_step.id}",
        json={
            "description": "Updated test step description",
            "sequence_number": 2
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated test step description"
    assert data["sequence_number"] == 2


@pytest.mark.asyncio
async def test_delete_test_step(client: AsyncClient, db_session: AsyncSession):
    """Test test step deletion via API"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    cmd_category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(cmd_category)
    await db_session.commit()
    await db_session.refresh(cmd_category)

    command = GenericCommand(
        template="Test command {Parameter}",
        category_id=cmd_category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    test_step = TestStep(
        test_specification_id=test_spec.id,
        action={
            "command_id": str(command.id),
            "populated_parameters": {"Parameter": "value1"}
        },
        expected_result={
            "command_id": str(command.id),
            "populated_parameters": {"Parameter": "value1"}
        },
        description="Test step description",
        sequence_number=1,
        created_by="test-user"
    )
    db_session.add(test_step)
    await db_session.commit()
    await db_session.refresh(test_step)

    # Delete test step
    response = await client.delete(f"/api/v1/test-specifications/{test_spec.id}/steps/{test_step.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Test step deleted successfully"

    # Verify deletion
    get_response = await client.get(f"/api/v1/test-specifications/{test_spec.id}/steps")
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_test_specification_validation_errors(client: AsyncClient, db_session: AsyncSession):
    """Test test specification validation errors"""
    # Test missing required fields
    response = await client.post(
        "/api/v1/test-specifications/",
        json={
            "name": "",  # Empty name
            "description": "Test description"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test invalid functional area
    response = await client.post(
        "/api/v1/test-specifications/",
        json={
            "name": "Test Specification",
            "description": "Test description",
            "functional_area": "INVALID_AREA",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_test_step_validation_errors(client: AsyncClient, db_session: AsyncSession):
    """Test test step validation errors"""
    # Create test data
    req_category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(req_category)
    await db_session.commit()
    await db_session.refresh(req_category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=req_category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    test_spec = TestSpecification(
        name="Test Specification",
        description="Test specification description",
        precondition="System is initialized",
        postcondition="Test completed successfully",
        test_data_description={"param1": "value1"},
        functional_area=FunctionalArea.UDS,
        created_by="test-user"
    )
    db_session.add(test_spec)
    await db_session.commit()
    await db_session.refresh(test_spec)

    # Test missing required fields
    response = await client.post(
        f"/api/v1/test-specifications/{test_spec.id}/steps",
        json={
            "description": "",  # Empty description
            "sequence_number": 1
        }
    )

    assert response.status_code == 422  # Validation error

    # Test invalid sequence number
    response = await client.post(
        f"/api/v1/test-specifications/{test_spec.id}/steps",
        json={
            "description": "Test step description",
            "sequence_number": -1  # Invalid sequence number
        }
    )

    assert response.status_code == 422  # Validation error
