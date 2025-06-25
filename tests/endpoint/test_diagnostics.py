import pytest

def test_available_routes():
    """Display all available routes in the application."""
    from fastapi import FastAPI
    from fastapi.routing import APIRoute
    from backend.main import app

    routes = [
        {"path": route.path, "name": route.name, "methods": route.methods}
        for route in app.routes
        if isinstance(route, APIRoute)
    ]

    assert False, f"Available routes: {routes}"


def test_direct_endpoint():
    """Test accessing endpoints directly - intentionally failing to show results."""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    results = {}
    paths_to_test = [
        "/",
        "/users",
        "/api/v1/users",
        "/auth/register",
        "/api/v1/auth/register",
        "/logs",
        "/api/v1/logs",
        "/foods",
        "/api/v1/foods"
    ]

    for path in paths_to_test:
        response = client.get(path)
        results[path] = response.status_code

    assert False, f"Endpoint results: {results}"


def test_model_fields():
    """Display schemas for key models - intentional failure to show details."""
    from sqlalchemy import inspect
    import backend.models as models

    model_info = {}
    model_classes = [
        models.User,
        models.Food,
        models.DailyLog,
        models.FoodEntry
    ]

    for model_class in model_classes:
        mapper = inspect(model_class)
        columns = {}
        for column in mapper.columns:
            columns[column.name] = {
                "type": str(column.type),
                "nullable": column.nullable
            }

        model_info[model_class.__name__] = columns

    assert False, f"Model information: {model_info}"
