import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.models import Food


def test_get_all_foods(client: TestClient, test_foods):
    """Test getting all foods (accessible without authentication)"""
    response = client.get("/api/v1/foods/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    food_names = [food["name"] for food in data]
    expected_names = [food.name for food in test_foods]

    for name in expected_names:
        assert name in food_names


def test_get_food_by_id(client: TestClient, test_foods):
    """Test getting a specific food by ID"""
    food_id = test_foods[0].id

    response = client.get(f"/api/v1/foods/{food_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == food_id
    assert data["name"] == test_foods[0].name


def test_get_nonexistent_food(client: TestClient):
    """Test getting a non-existent food"""
    response = client.get("/api/v1/foods/9999")
    assert response.status_code == 404
    assert "Food not found" in response.json()["detail"]


def test_create_food_admin(admin_client: TestClient, db_session: Session):
    """Test creating a new food as admin"""
    food_data = {
        "name": "Salmon",
        "calories": 208,
        "protein": 20,
        "carbs": 0,
        "fat": 13,
        "serving_size": 100.0,
        "unit": "g",
        "manufacturer": "Test Manufacturer"
    }

    response = admin_client.post("/api/v1/foods/", json=food_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == food_data["name"]
    assert data["calories"] == food_data["calories"]
    assert data["protein"] == food_data["protein"]
    assert data["carbs"] == food_data["carbs"]
    assert data["fat"] == food_data["fat"]
    assert data["serving_size"] == food_data["serving_size"]
    assert data["unit"] == food_data["unit"]
    assert data["manufacturer"] == food_data["manufacturer"]

    created_food = db_session.query(Food).filter(Food.id == data["id"]).first()
    assert created_food is not None
    assert created_food.name == food_data["name"]


def test_create_food_non_admin(authorized_client: TestClient):
    """Test creating a food as non-admin user"""
    food_data = {
        "name": "Avocado",
        "calories": 160,
        "protein": 2,
        "carbs": 8.5,
        "fat": 14.7,
        "serving_size": 100.0,
        "unit": "g",
        "manufacturer": "Test Manufacturer"
    }

    response = authorized_client.post("/api/v1/foods/", json=food_data)
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_create_food_unauthorized(client: TestClient):
    """Test creating a food without authentication"""
    food_data = {
        "name": "Avocado",
        "calories": 160,
        "protein": 2,
        "carbs": 8.5,
        "fat": 14.7,
        "serving_size": 100.0,
        "unit": "g",
        "manufacturer": "Test Manufacturer"
    }

    # Corrected URL to /api/v1/foods/
    response = client.post("/api/v1/foods/", json=food_data)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_update_food_admin(admin_client: TestClient, test_foods, db_session: Session):
    """Test updating a food as admin"""
    food_id = test_foods[0].id
    update_data = {
        "name": "Updated Apple",
        "calories": 60,
        "protein": 0.4,
        "carbs": 15,
        "fat": 0.3,
        "serving_size": 200.0,
        "unit": "g",
        "manufacturer": "Updated Manufacturer"
    }

    response = admin_client.put(f"/api/v1/foods/{food_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == food_id
    assert data["name"] == update_data["name"]
    assert data["calories"] == update_data["calories"]
    assert data["protein"] == update_data["protein"]
    assert data["carbs"] == update_data["carbs"]
    assert data["fat"] == update_data["fat"]
    assert data["serving_size"] == update_data["serving_size"]
    assert data["unit"] == update_data["unit"]
    assert data["manufacturer"] == update_data["manufacturer"]

    updated_food = db_session.query(Food).filter(Food.id == food_id).first()
    assert updated_food.name == update_data["name"]


def test_update_food_non_admin(authorized_client: TestClient, test_foods):
    """Test updating a food as non-admin user"""
    food_id = test_foods[0].id
    update_data = {
        "name": "Hacked Apple",
        "calories": 999
    }

    response = authorized_client.put(f"/api/v1/foods/{food_id}", json=update_data)
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_delete_food_admin(admin_client: TestClient, db_session: Session):
    """Test deleting a food as admin"""
    food_to_delete = Food(
        name="Temporary Food",
        calories=100,
        protein=1,
        carbs=10,
        fat=5,
        serving_size=1.0,
        unit="serving",
        manufacturer="Test Manufacturer"
    )
    db_session.add(food_to_delete)
    db_session.commit()
    db_session.refresh(food_to_delete)

    food_id = food_to_delete.id

    response = admin_client.delete(f"/api/v1/foods/{food_id}")
    assert response.status_code == 204

    deleted_food = db_session.query(Food).filter(Food.id == food_id).first()
    assert deleted_food is None


def test_delete_food_non_admin(authorized_client: TestClient, test_foods):
    """Test deleting a food as non-admin user"""
    food_id = test_foods[0].id

    response = authorized_client.delete(f"/api/v1/foods/{food_id}")
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_search_foods(client: TestClient, test_foods, db_session: Session):
    """Test searching for foods by name"""
    additional_foods = [
        Food(name="Apple Juice", calories=45, protein=0.1, carbs=11.5, fat=0.1,
             serving_size=100.0, unit="ml", manufacturer="Test Manufacturer"),
        Food(name="Apple Pie", calories=237, protein=2.4, carbs=34, fat=11,
             serving_size=100.0, unit="g", manufacturer="Test Manufacturer"),
        Food(name="Pineapple", calories=50, protein=0.5, carbs=13, fat=0.1,
             serving_size=100.0, unit="g", manufacturer="Test Manufacturer")
    ]
    for food in additional_foods:
        db_session.add(food)
    db_session.commit()

    # Search for "apple"
    response = client.get("/api/v1/foods/search/?query=apple")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    food_names = [f["name"].lower() for f in data]
    assert all("apple" in n for n in food_names)

    # Search for exact name
    response = client.get("/api/v1/foods/search/?query=Apple%20Pie")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert "Apple Pie" in [f["name"] for f in data]

    # Search with no results
    response = client.get("/api/v1/foods/search/?query=NonexistentFood")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
