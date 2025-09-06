"""
API endpoint tests for GenericCommand and CommandCategory management.

This module tests all RESTful endpoints for generic commands, command categories,
and command-parameter relationships with comprehensive test coverage.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.command import GenericCommand
from app.models.category import CommandCategory
from app.models.parameter import Parameter
from app.models.category import ParameterCategory
from app.schemas.command import GenericCommandCreate, CommandCategoryCreate


@pytest.mark.asyncio
async def test_create_generic_command(client: AsyncClient, db_session: AsyncSession):
    """Test generic command creation via API"""
    # Create command category first
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create parameter category and parameter
    param_category = ParameterCategory(
        name="Test Parameter Category",
        description="Test parameter category description",
        created_by="test-user"
    )
    db_session.add(param_category)
    await db_session.commit()
    await db_session.refresh(param_category)

    parameter = Parameter(
        name="Test Parameter",
        category_id=param_category.id,
        has_variants=False,
        default_value="default",
        description="Test parameter description",
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()
    await db_session.refresh(parameter)

    # Create generic command
    response = await client.post(
        "/api/v1/commands/",
        json={
            "template": "Test command with {Test Parameter}",
            "category_id": str(category.id),
            "description": "Test command description",
            "required_parameter_ids": [str(parameter.id)],
            "created_by": "test-user"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["template"] == "Test command with {Test Parameter}"
    assert data["category_id"] == str(category.id)
    assert len(data["required_parameter_ids"]) == 1
    assert data["required_parameter_ids"][0] == str(parameter.id)


@pytest.mark.asyncio
async def test_create_generic_command_with_multiple_parameters(client: AsyncClient, db_session: AsyncSession):
    """Test generic command creation with multiple parameters"""
    # Create command category first
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create parameter category and parameters
    param_category = ParameterCategory(
        name="Test Parameter Category",
        description="Test parameter category description",
        created_by="test-user"
    )
    db_session.add(param_category)
    await db_session.commit()
    await db_session.refresh(param_category)

    param1 = Parameter(
        name="Parameter1",
        category_id=param_category.id,
        has_variants=False,
        default_value="default1",
        description="Test parameter 1 description",
        created_by="test-user"
    )
    param2 = Parameter(
        name="Parameter2",
        category_id=param_category.id,
        has_variants=False,
        default_value="default2",
        description="Test parameter 2 description",
        created_by="test-user"
    )
    db_session.add(param1)
    db_session.add(param2)
    await db_session.commit()
    await db_session.refresh(param1)
    await db_session.refresh(param2)

    # Create generic command with multiple parameters
    response = await client.post(
        "/api/v1/commands/",
        json={
            "template": "Test command with {Parameter1} and {Parameter2}",
            "category_id": str(category.id),
            "description": "Test command with multiple parameters description",
            "required_parameter_ids": [str(param1.id), str(param2.id)],
            "created_by": "test-user"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["template"] == "Test command with {Parameter1} and {Parameter2}"
    assert len(data["required_parameter_ids"]) == 2


@pytest.mark.asyncio
async def test_get_generic_commands(client: AsyncClient, db_session: AsyncSession):
    """Test getting generic commands via API"""
    # Create test data
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    command = GenericCommand(
        template="Test command template",
        category_id=category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()

    # Get generic commands
    response = await client.get("/api/v1/commands/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["template"] == "Test command template"


@pytest.mark.asyncio
async def test_get_generic_commands_with_pagination(client: AsyncClient, db_session: AsyncSession):
    """Test getting generic commands with pagination"""
    # Create test data
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create multiple commands
    for i in range(5):
        command = GenericCommand(
            template=f"Test command template {i}",
            category_id=category.id,
            description=f"Test command description {i}",
            created_by="test-user"
        )
        db_session.add(command)
    await db_session.commit()

    # Get commands with pagination
    response = await client.get("/api/v1/commands/?skip=0&limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_get_generic_commands_by_category(client: AsyncClient, db_session: AsyncSession):
    """Test getting generic commands filtered by category"""
    # Create test categories
    category1 = CommandCategory(
        name="Category 1",
        description="Test command category 1",
        created_by="test-user"
    )
    category2 = CommandCategory(
        name="Category 2",
        description="Test command category 2",
        created_by="test-user"
    )
    db_session.add(category1)
    db_session.add(category2)
    await db_session.commit()
    await db_session.refresh(category1)
    await db_session.refresh(category2)

    # Create commands for different categories
    cmd1 = GenericCommand(
        template="Command 1 template",
        category_id=category1.id,
        description="Test command 1 description",
        created_by="test-user"
    )
    cmd2 = GenericCommand(
        template="Command 2 template",
        category_id=category2.id,
        description="Test command 2 description",
        created_by="test-user"
    )
    db_session.add(cmd1)
    db_session.add(cmd2)
    await db_session.commit()

    # Get commands by category
    response = await client.get(f"/api/v1/commands/?category_id={category1.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["template"] == "Command 1 template"


@pytest.mark.asyncio
async def test_get_generic_command_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific generic command by ID"""
    # Create test data
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    command = GenericCommand(
        template="Test command template",
        category_id=category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    # Get command by ID
    response = await client.get(f"/api/v1/commands/{command.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["template"] == "Test command template"
    assert data["id"] == str(command.id)


@pytest.mark.asyncio
async def test_get_generic_command_not_found(client: AsyncClient):
    """Test getting non-existent generic command"""
    response = await client.get("/api/v1/commands/non-existent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_generic_command(client: AsyncClient, db_session: AsyncSession):
    """Test generic command update via API"""
    # Create test data
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    command = GenericCommand(
        template="Test command template",
        category_id=category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    # Update command
    response = await client.put(
        f"/api/v1/commands/{command.id}",
        json={
            "template": "Updated command template",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["template"] == "Updated command template"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_generic_command_not_found(client: AsyncClient):
    """Test updating non-existent generic command"""
    response = await client.put(
        "/api/v1/commands/non-existent-id",
        json={
            "template": "Updated command template"
        }
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_generic_command(client: AsyncClient, db_session: AsyncSession):
    """Test generic command deletion via API"""
    # Create test data
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    command = GenericCommand(
        template="Test command template",
        category_id=category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)

    # Delete command
    response = await client.delete(f"/api/v1/commands/{command.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Command deleted successfully"

    # Verify deletion
    get_response = await client.get(f"/api/v1/commands/{command.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_generic_command_not_found(client: AsyncClient):
    """Test deleting non-existent generic command"""
    response = await client.delete("/api/v1/commands/non-existent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_command_category(client: AsyncClient, db_session: AsyncSession):
    """Test command category creation via API"""
    response = await client.post(
        "/api/v1/commands/categories",
        json={
            "name": "Test Command Category",
            "description": "Test command category description",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Command Category"
    assert data["description"] == "Test command category description"


@pytest.mark.asyncio
async def test_get_command_categories(client: AsyncClient, db_session: AsyncSession):
    """Test getting command categories via API"""
    # Create test categories
    category1 = CommandCategory(
        name="Category 1",
        description="Test command category 1",
        created_by="test-user"
    )
    category2 = CommandCategory(
        name="Category 2",
        description="Test command category 2",
        created_by="test-user"
    )
    db_session.add(category1)
    db_session.add(category2)
    await db_session.commit()

    # Get categories
    response = await client.get("/api/v1/commands/categories")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_command_category_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific command category by ID"""
    # Create test category
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Get category by ID
    response = await client.get(f"/api/v1/commands/categories/{category.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Command Category"
    assert data["id"] == str(category.id)


@pytest.mark.asyncio
async def test_update_command_category(client: AsyncClient, db_session: AsyncSession):
    """Test command category update via API"""
    # Create test category
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Update category
    response = await client.put(
        f"/api/v1/commands/categories/{category.id}",
        json={
            "name": "Updated Command Category",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Command Category"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_command_category(client: AsyncClient, db_session: AsyncSession):
    """Test command category deletion via API"""
    # Create test category
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Delete category
    response = await client.delete(f"/api/v1/commands/categories/{category.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Command category deleted successfully"

    # Verify deletion
    get_response = await client.get(f"/api/v1/commands/categories/{category.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_command_category_with_commands(client: AsyncClient, db_session: AsyncSession):
    """Test deleting command category that has commands"""
    # Create test data
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    command = GenericCommand(
        template="Test command template",
        category_id=category.id,
        description="Test command description",
        created_by="test-user"
    )
    db_session.add(command)
    await db_session.commit()

    # Try to delete category with commands
    response = await client.delete(f"/api/v1/commands/categories/{category.id}")

    assert response.status_code == 409
    assert "commands" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_search_generic_commands(client: AsyncClient, db_session: AsyncSession):
    """Test searching generic commands"""
    # Create test data
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create commands with different templates
    cmd1 = GenericCommand(
        template="Authentication command template",
        category_id=category.id,
        description="Authentication command description",
        created_by="test-user"
    )
    cmd2 = GenericCommand(
        template="Authorization command template",
        category_id=category.id,
        description="Authorization command description",
        created_by="test-user"
    )
    db_session.add(cmd1)
    db_session.add(cmd2)
    await db_session.commit()

    # Search for commands
    response = await client.get("/api/v1/commands/search/?q=Authentication")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["template"] == "Authentication command template"


@pytest.mark.asyncio
async def test_search_generic_commands_by_category(client: AsyncClient, db_session: AsyncSession):
    """Test searching generic commands by category"""
    # Create test categories
    category1 = CommandCategory(
        name="UDS Category",
        description="UDS command category description",
        created_by="test-user"
    )
    category2 = CommandCategory(
        name="Communication Category",
        description="Communication command category description",
        created_by="test-user"
    )
    db_session.add(category1)
    db_session.add(category2)
    await db_session.commit()
    await db_session.refresh(category1)
    await db_session.refresh(category2)

    # Create commands for different categories
    cmd1 = GenericCommand(
        template="UDS command template",
        category_id=category1.id,
        description="UDS command description",
        created_by="test-user"
    )
    cmd2 = GenericCommand(
        template="Communication command template",
        category_id=category2.id,
        description="Communication command description",
        created_by="test-user"
    )
    db_session.add(cmd1)
    db_session.add(cmd2)
    await db_session.commit()

    # Search for commands by category
    response = await client.get(f"/api/v1/commands/search/?q=command&category_id={category1.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["template"] == "UDS command template"


@pytest.mark.asyncio
async def test_generic_command_validation_errors(client: AsyncClient, db_session: AsyncSession):
    """Test generic command validation errors"""
    # Test missing required fields
    response = await client.post(
        "/api/v1/commands/",
        json={
            "template": "",  # Empty template
            "description": "Test description"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test invalid category ID
    response = await client.post(
        "/api/v1/commands/",
        json={
            "template": "Test command template",
            "description": "Test description",
            "category_id": "invalid-uuid",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test invalid parameter ID
    response = await client.post(
        "/api/v1/commands/",
        json={
            "template": "Test command template",
            "description": "Test description",
            "required_parameter_ids": ["invalid-uuid"],
            "created_by": "test-user"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_command_category_validation_errors(client: AsyncClient):
    """Test command category validation errors"""
    # Test missing required fields
    response = await client.post(
        "/api/v1/commands/categories",
        json={
            "name": "",  # Empty name
            "description": "Test description"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test duplicate name
    # First create a category
    response1 = await client.post(
        "/api/v1/commands/categories",
        json={
            "name": "Duplicate Category",
            "description": "Test description",
            "created_by": "test-user"
        }
    )
    assert response1.status_code == 200

    # Try to create another with same name
    response2 = await client.post(
        "/api/v1/commands/categories",
        json={
            "name": "Duplicate Category",
            "description": "Test description",
            "created_by": "test-user"
        }
    )

    assert response2.status_code == 409  # Conflict error


@pytest.mark.asyncio
async def test_command_template_validation(client: AsyncClient, db_session: AsyncSession):
    """Test command template validation"""
    # Create command category first
    category = CommandCategory(
        name="Test Command Category",
        description="Test command category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Test invalid template format
    response = await client.post(
        "/api/v1/commands/",
        json={
            "template": "Invalid template {",  # Missing closing brace
            "category_id": str(category.id),
            "description": "Test description",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test template with invalid characters
    response = await client.post(
        "/api/v1/commands/",
        json={
            "template": "Invalid template with <script>alert('xss')</script>",
            "category_id": str(category.id),
            "description": "Test description",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 422  # Validation error
