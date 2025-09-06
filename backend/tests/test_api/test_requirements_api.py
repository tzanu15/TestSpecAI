"""
API endpoint tests for Requirement and RequirementCategory management.

This module tests all RESTful endpoints for requirements and requirement categories
with comprehensive test coverage including CRUD operations, validation, and error handling.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.requirement import Requirement
from app.models.category import RequirementCategory
from app.schemas.requirement import RequirementCreate, RequirementUpdate


@pytest.mark.asyncio
async def test_create_requirement(client: AsyncClient, db_session: AsyncSession):
    """Test requirement creation via API"""
    # Create category first
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create requirement
    response = await client.post(
        "/api/v1/requirements/",
        json={
            "title": "Test Requirement",
            "description": "Test requirement description",
            "category_id": str(category.id),
            "source": "manual",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Requirement"
    assert data["category_id"] == str(category.id)
    assert data["source"] == "manual"
    assert data["created_by"] == "test-user"


@pytest.mark.asyncio
async def test_create_requirement_with_metadata(client: AsyncClient, db_session: AsyncSession):
    """Test requirement creation with metadata"""
    # Create category first
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create requirement with metadata
    response = await client.post(
        "/api/v1/requirements/",
        json={
            "title": "Test Requirement with Metadata",
            "description": "Test requirement with metadata description",
            "category_id": str(category.id),
            "source": "document",
            "metadata": {
                "priority": "high",
                "complexity": "medium",
                "version": "1.0"
            },
            "created_by": "test-user"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Requirement with Metadata"
    # Metadata is stored and can be retrieved
    assert "metadata" in data or "metadata_json" in data


@pytest.mark.asyncio
async def test_get_requirements(client: AsyncClient, db_session: AsyncSession):
    """Test getting requirements via API"""
    # Create test data
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()

    # Get requirements
    response = await client.get("/api/v1/requirements/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test Requirement"


@pytest.mark.asyncio
async def test_get_requirements_with_pagination(client: AsyncClient, db_session: AsyncSession):
    """Test getting requirements with pagination"""
    # Create test data
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create multiple requirements
    for i in range(5):
        requirement = Requirement(
            title=f"Test Requirement {i}",
            description=f"Test requirement description {i}",
            category_id=category.id,
            source="manual",
            created_by="test-user"
        )
        db_session.add(requirement)
    await db_session.commit()

    # Get requirements with pagination
    response = await client.get("/api/v1/requirements/?skip=0&limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_get_requirements_by_category(client: AsyncClient, db_session: AsyncSession):
    """Test getting requirements filtered by category"""
    # Create test categories
    category1 = RequirementCategory(
        name="Category 1",
        description="Test category 1",
        created_by="test-user"
    )
    category2 = RequirementCategory(
        name="Category 2",
        description="Test category 2",
        created_by="test-user"
    )
    db_session.add(category1)
    db_session.add(category2)
    await db_session.commit()
    await db_session.refresh(category1)
    await db_session.refresh(category2)

    # Create requirements for different categories
    req1 = Requirement(
        title="Requirement 1",
        description="Test requirement 1",
        category_id=category1.id,
        source="manual",
        created_by="test-user"
    )
    req2 = Requirement(
        title="Requirement 2",
        description="Test requirement 2",
        category_id=category2.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(req1)
    db_session.add(req2)
    await db_session.commit()

    # Get requirements by category
    response = await client.get(f"/api/v1/requirements/?category_id={category1.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Requirement 1"


@pytest.mark.asyncio
async def test_get_requirements_by_search(client: AsyncClient, db_session: AsyncSession):
    """Test getting requirements with search"""
    # Create test data
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create requirements with different titles
    req1 = Requirement(
        title="Authentication Requirement",
        description="Test authentication requirement",
        category_id=category.id,
        source="manual",
        created_by="test-user"
    )
    req2 = Requirement(
        title="Authorization Requirement",
        description="Test authorization requirement",
        category_id=category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(req1)
    db_session.add(req2)
    await db_session.commit()

    # Search for requirements
    response = await client.get("/api/v1/requirements/?search=Authentication")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Authentication Requirement"


@pytest.mark.asyncio
async def test_get_requirement_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific requirement by ID"""
    # Create test data
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    # Get requirement by ID
    response = await client.get(f"/api/v1/requirements/{requirement.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Requirement"
    assert data["id"] == str(requirement.id)


@pytest.mark.asyncio
async def test_get_requirement_not_found(client: AsyncClient):
    """Test getting non-existent requirement"""
    response = await client.get("/api/v1/requirements/550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_requirement(client: AsyncClient, db_session: AsyncSession):
    """Test requirement update via API"""
    # Create test data
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    # Update requirement
    response = await client.put(
        f"/api/v1/requirements/{requirement.id}",
        json={
            "title": "Updated Requirement",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Requirement"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_requirement_not_found(client: AsyncClient):
    """Test updating non-existent requirement"""
    response = await client.put(
        "/api/v1/requirements/550e8400-e29b-41d4-a716-446655440000",
        json={
            "title": "Updated Requirement"
        }
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_requirement(client: AsyncClient, db_session: AsyncSession):
    """Test requirement deletion via API"""
    # Create test data
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)

    # Delete requirement
    response = await client.delete(f"/api/v1/requirements/{requirement.id}")

    assert response.status_code == 204

    # Verify deletion
    get_response = await client.get(f"/api/v1/requirements/{requirement.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_requirement_not_found(client: AsyncClient):
    """Test deleting non-existent requirement"""
    response = await client.delete("/api/v1/requirements/550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_requirement_category(client: AsyncClient, db_session: AsyncSession):
    """Test requirement category creation via API"""
    response = await client.post(
        "/api/v1/requirements/categories/",
        json={
            "name": "Test Category",
            "description": "Test category description",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "Test category description"


@pytest.mark.asyncio
async def test_get_requirement_categories(client: AsyncClient, db_session: AsyncSession):
    """Test getting requirement categories via API"""
    # Create test categories
    category1 = RequirementCategory(
        name="Category 1",
        description="Test category 1",
        created_by="test-user"
    )
    category2 = RequirementCategory(
        name="Category 2",
        description="Test category 2",
        created_by="test-user"
    )
    db_session.add(category1)
    db_session.add(category2)
    await db_session.commit()

    # Get categories
    response = await client.get("/api/v1/requirements/categories/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_requirement_category_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific requirement category by ID"""
    # Create test category
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Get category by ID
    response = await client.get(f"/api/v1/requirements/categories/{category.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["id"] == str(category.id)


@pytest.mark.asyncio
async def test_update_requirement_category(client: AsyncClient, db_session: AsyncSession):
    """Test requirement category update via API"""
    # Create test category
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Update category
    response = await client.put(
        f"/api/v1/requirements/categories/{category.id}",
        json={
            "name": "Updated Category",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_requirement_category(client: AsyncClient, db_session: AsyncSession):
    """Test requirement category deletion via API"""
    # Create test category
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Delete category
    response = await client.delete(f"/api/v1/requirements/categories/{category.id}")

    assert response.status_code == 204

    # Verify deletion
    get_response = await client.get(f"/api/v1/requirements/categories/{category.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_requirement_category_with_requirements(client: AsyncClient, db_session: AsyncSession):
    """Test deleting requirement category that has requirements"""
    # Create test data
    category = RequirementCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    requirement = Requirement(
        title="Test Requirement",
        description="Test requirement description",
        category_id=category.id,
        source="manual",
        created_by="test-user"
    )
    db_session.add(requirement)
    await db_session.commit()

    # Try to delete category with requirements
    response = await client.delete(f"/api/v1/requirements/categories/{category.id}")

    assert response.status_code == 400
    assert "requirements" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_requirement_validation_errors(client: AsyncClient, db_session: AsyncSession):
    """Test requirement validation errors"""
    # Test missing required fields
    response = await client.post(
        "/api/v1/requirements/",
        json={
            "title": "",  # Empty title
            "description": "Test description"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test invalid category ID
    response = await client.post(
        "/api/v1/requirements/",
        json={
            "title": "Test Requirement",
            "description": "Test description",
            "category_id": "invalid-uuid",
            "source": "manual",
            "created_by": "test-user"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_requirement_category_validation_errors(client: AsyncClient):
    """Test requirement category validation errors"""
    # Test missing required fields
    response = await client.post(
        "/api/v1/requirements/categories/",
        json={
            "name": "",  # Empty name
            "description": "Test description"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test duplicate name
    # First create a category
    response1 = await client.post(
        "/api/v1/requirements/categories/",
        json={
            "name": "Duplicate Category",
            "description": "Test description",
            "created_by": "test-user"
        }
    )
    assert response1.status_code == 201

    # Try to create another with same name
    response2 = await client.post(
        "/api/v1/requirements/categories/",
        json={
            "name": "Duplicate Category",
            "description": "Test description",
            "created_by": "test-user"
        }
    )

    assert response2.status_code == 400  # Conflict error
