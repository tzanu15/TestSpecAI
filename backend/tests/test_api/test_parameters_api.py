"""
API endpoint tests for Parameter and ParameterVariant management.

This module tests all RESTful endpoints for parameters, parameter categories,
and parameter variants with comprehensive test coverage.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parameter import Parameter, ParameterVariant
from app.models.category import ParameterCategory
from app.schemas.parameter import ParameterCreate, ParameterCategoryCreate, ParameterVariantCreate


@pytest.mark.asyncio
async def test_create_parameter(client: AsyncClient, db_session: AsyncSession):
    """Test parameter creation via API"""
    # Create category first
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create parameter
    response = await client.post(
        "/api/v1/parameters/",
        json={
            "name": "Test Parameter",
            "description": "Test parameter description",
            "category_id": str(category.id),
            "has_variants": False,
            "default_value": "default"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Parameter"
    assert data["category_id"] == str(category.id)
    assert data["has_variants"] is False
    assert data["default_value"] == "default"


@pytest.mark.asyncio
async def test_create_parameter_with_variants(client: AsyncClient, db_session: AsyncSession):
    """Test parameter creation with variants via API"""
    # Create category first
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create parameter with variants
    response = await client.post(
        "/api/v1/parameters/",
        json={
            "name": "Test Parameter with Variants",
            "description": "Test parameter with variants description",
            "category_id": str(category.id),
            "has_variants": True,
            "variants": [
                {
                    "manufacturer": "BMW",
                    "value": "Level 1",
                    "description": "BMW Level 1"
                },
                {
                    "manufacturer": "VW",
                    "value": "Level 2",
                    "description": "VW Level 2"
                }
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Parameter with Variants"
    assert data["has_variants"] is True
    assert data["default_value"] is None
    assert len(data["variants"]) == 2


@pytest.mark.asyncio
async def test_get_parameters(client: AsyncClient, db_session: AsyncSession):
    """Test getting parameters via API"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    parameter = Parameter(
        name="Test Parameter",
        description="Test parameter description",
        category_id=category.id,
        has_variants=False,
        default_value="default",
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()

    # Get parameters
    response = await client.get("/api/v1/parameters/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Parameter"
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_parameters_with_filters(client: AsyncClient, db_session: AsyncSession):
    """Test getting parameters with advanced filters"""
    # Create test data
    category1 = ParameterCategory(
        name="Category 1",
        description="Category 1 description",
        created_by="test-user"
    )
    category2 = ParameterCategory(
        name="Category 2",
        description="Category 2 description",
        created_by="test-user"
    )
    db_session.add_all([category1, category2])
    await db_session.commit()
    await db_session.refresh(category1)
    await db_session.refresh(category2)

    # Create parameters
    param1 = Parameter(
        name="Parameter 1",
        description="Parameter 1 description",
        category_id=category1.id,
        has_variants=False,
        default_value="default1",
        created_by="test-user"
    )
    param2 = Parameter(
        name="Parameter 2",
        description="Parameter 2 description",
        category_id=category2.id,
        has_variants=True,
        created_by="test-user"
    )
    db_session.add_all([param1, param2])
    await db_session.commit()

    # Test filter by category
    response = await client.get(f"/api/v1/parameters/?category_id={category1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Parameter 1"

    # Test filter by has_variants
    response = await client.get("/api/v1/parameters/?has_variants=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Parameter 2"

    # Test search
    response = await client.get("/api/v1/parameters/?search=Parameter 1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Parameter 1"


@pytest.mark.asyncio
async def test_get_parameter_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific parameter by ID"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    parameter = Parameter(
        name="Test Parameter",
        description="Test parameter description",
        category_id=category.id,
        has_variants=False,
        default_value="default",
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()
    await db_session.refresh(parameter)

    # Get parameter by ID
    response = await client.get(f"/api/v1/parameters/{parameter.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Parameter"
    assert data["id"] == str(parameter.id)


@pytest.mark.asyncio
async def test_update_parameter(client: AsyncClient, db_session: AsyncSession):
    """Test parameter update via API"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    parameter = Parameter(
        name="Test Parameter",
        description="Test parameter description",
        category_id=category.id,
        has_variants=False,
        default_value="default",
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()
    await db_session.refresh(parameter)

    # Update parameter
    response = await client.put(
        f"/api/v1/parameters/{parameter.id}",
        json={
            "name": "Updated Parameter",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Parameter"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_parameter(client: AsyncClient, db_session: AsyncSession):
    """Test parameter deletion via API"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    parameter = Parameter(
        name="Test Parameter",
        description="Test parameter description",
        category_id=category.id,
        has_variants=False,
        default_value="default",
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()
    await db_session.refresh(parameter)

    # Delete parameter
    response = await client.delete(f"/api/v1/parameters/{parameter.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Parameter deleted successfully"

    # Verify parameter is soft deleted
    response = await client.get(f"/api/v1/parameters/{parameter.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_parameter_not_found(client: AsyncClient):
    """Test getting non-existent parameter"""
    response = await client.get("/api/v1/parameters/non-existent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_parameter_category(client: AsyncClient, db_session: AsyncSession):
    """Test parameter category creation via API"""
    response = await client.post(
        "/api/v1/parameters/categories/",
        json={
            "name": "Test Category",
            "description": "Test category description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "Test category description"


@pytest.mark.asyncio
async def test_get_parameter_categories(client: AsyncClient, db_session: AsyncSession):
    """Test getting parameter categories via API"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()

    # Get categories
    response = await client.get("/api/v1/parameters/categories/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Category"


@pytest.mark.asyncio
async def test_create_parameter_variant(client: AsyncClient, db_session: AsyncSession):
    """Test parameter variant creation via API"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    parameter = Parameter(
        name="Test Parameter",
        description="Test parameter description",
        category_id=category.id,
        has_variants=True,
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()
    await db_session.refresh(parameter)

    # Create variant
    response = await client.post(
        f"/api/v1/parameters/{parameter.id}/variants/",
        json={
            "manufacturer": "BMW",
            "value": "Level 1",
            "description": "BMW Level 1"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["manufacturer"] == "BMW"
    assert data["value"] == "Level 1"
    assert data["parameter_id"] == str(parameter.id)


@pytest.mark.asyncio
async def test_get_parameter_variants(client: AsyncClient, db_session: AsyncSession):
    """Test getting parameter variants via API"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    parameter = Parameter(
        name="Test Parameter",
        description="Test parameter description",
        category_id=category.id,
        has_variants=True,
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()
    await db_session.refresh(parameter)

    variant = ParameterVariant(
        parameter_id=parameter.id,
        manufacturer="BMW",
        value="Level 1",
        description="BMW Level 1",
        created_by="test-user"
    )
    db_session.add(variant)
    await db_session.commit()

    # Get variants
    response = await client.get(f"/api/v1/parameters/{parameter.id}/variants/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["manufacturer"] == "BMW"
    assert data[0]["value"] == "Level 1"


@pytest.mark.asyncio
async def test_parameter_validation_errors(client: AsyncClient, db_session: AsyncSession):
    """Test parameter validation error handling"""
    # Test creating parameter without required fields
    response = await client.post(
        "/api/v1/parameters/",
        json={
            "name": "",  # Empty name
            "description": "Test description"
        }
    )

    assert response.status_code == 422  # Validation error

    # Test creating parameter with non-existent category
    response = await client.post(
        "/api/v1/parameters/",
        json={
            "name": "Test Parameter",
            "description": "Test description",
            "category_id": "non-existent-id",
            "has_variants": False,
            "default_value": "default"
        }
    )

    assert response.status_code == 400  # Bad request


@pytest.mark.asyncio
async def test_parameter_variant_validation_errors(client: AsyncClient, db_session: AsyncSession):
    """Test parameter variant validation error handling"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    parameter = Parameter(
        name="Test Parameter",
        description="Test parameter description",
        category_id=category.id,
        has_variants=True,
        created_by="test-user"
    )
    db_session.add(parameter)
    await db_session.commit()
    await db_session.refresh(parameter)

    # Test creating variant without required fields
    response = await client.post(
        f"/api/v1/parameters/{parameter.id}/variants/",
        json={
            "manufacturer": "",  # Empty manufacturer
            "value": "Level 1"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_parameter_advanced_sorting(client: AsyncClient, db_session: AsyncSession):
    """Test parameter advanced sorting functionality"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create parameters with different names for sorting
    param1 = Parameter(
        name="Alpha Parameter",
        description="First parameter",
        category_id=category.id,
        has_variants=False,
        default_value="default1",
        created_by="test-user"
    )
    param2 = Parameter(
        name="Beta Parameter",
        description="Second parameter",
        category_id=category.id,
        has_variants=False,
        default_value="default2",
        created_by="test-user"
    )
    db_session.add_all([param1, param2])
    await db_session.commit()

    # Test sorting by name ascending
    response = await client.get("/api/v1/parameters/?sort_by=name&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["name"] == "Alpha Parameter"
    assert data["items"][1]["name"] == "Beta Parameter"

    # Test sorting by name descending
    response = await client.get("/api/v1/parameters/?sort_by=name&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["name"] == "Beta Parameter"
    assert data["items"][1]["name"] == "Alpha Parameter"


@pytest.mark.asyncio
async def test_parameter_pagination(client: AsyncClient, db_session: AsyncSession):
    """Test parameter pagination functionality"""
    # Create test data
    category = ParameterCategory(
        name="Test Category",
        description="Test category description",
        created_by="test-user"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create multiple parameters
    parameters = []
    for i in range(5):
        param = Parameter(
            name=f"Parameter {i}",
            description=f"Parameter {i} description",
            category_id=category.id,
            has_variants=False,
            default_value=f"default{i}",
            created_by="test-user"
        )
        parameters.append(param)

    db_session.add_all(parameters)
    await db_session.commit()

    # Test pagination
    response = await client.get("/api/v1/parameters/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total_pages"] == 3

    # Test second page
    response = await client.get("/api/v1/parameters/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 2
