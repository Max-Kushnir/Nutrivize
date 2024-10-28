import pytest
from pydantic import ValidationError

from nutrition_logger.schema.daily_log import DailyLogCreate, DailyLogResponse
from nutrition_logger.schema.user import UserCreate, UserResponse
from nutrition_logger.schema.food import FoodCreate, FoodResponse
from nutrition_logger.schema.food_entry import FoodEntryCreate, FoodEntryResponse

UserResponse.model_rebuild()

# testing validation
def test_valid_user():
    valid_user = UserCreate(username="Maxime_Kushnir", email="maxekushnir@gmail.com")
    assert valid_user.model_dump() == {
        "username": "Maxime_Kushnir",
        "email": "maxekushnir@gmail.com"
    }
    
@pytest.mark.parametrize("field,invalid_value,error_message", [("username", "", "String should have at least 1 character"), ("email", "Maxime_Kushnir", "value is not a valid email address")])
def test_invalid_user(field, invalid_value, error_message):
    valid_data = {"username":"Maxime_Kushnir", "email":"maxekushnir@gmail.com"}
    invalid_data = valid_data.copy()
    invalid_data[field] = invalid_value

    with pytest.raises(ValidationError) as error:
        UserCreate(**invalid_data)

    assert error_message in str(error)

def test_valid_food():
    valid_food = FoodCreate(
        name="Banana",
        manufacturer="example_shop",
        serving_size=1,
        unit="Banana",
        calories=80,
        protein=1.3,
        carbs=27,
        fat=0.4
    )
    
    assert valid_food.model_dump() == {
        "name":"Banana",
        "manufacturer":"example_shop",
        "serving_size":1,
        "unit":"Banana",
        "calories":80,
        "protein":1.3,
        "carbs":27,
        "fat":0.4
    }

@pytest.mark.parametrize("field,invalid_value,error_message", [
    ("name", "", "String should have at least 1 character"),
    ("manufacturer", "", "String should have at least 1 character"),
    ("serving_size", "-1", "Input should be greater than 0"),
    ("unit", "", "String should have at least 1 character"),
    ("calories", "-1", "Input should be greater than or equal to 0"),
    ("protein", "-1", "Input should be greater than or equal to 0"),
    ("carbs", "-1", "Input should be greater than or equal to 0"),
    ("fat", "-1", "Input should be greater than or equal to 0"),
])
def test_invalid_food(field, invalid_value, error_message):
    valid_data = {
        "name":"Banana",
        "manufacturer":"example_shop",
        "serving_size":1,
        "unit":"Banana",
        "calories":80,
        "protein":1.3,
        "carbs":27,
        "fat":0.4
    }
    invalid_data = valid_data.copy()
    invalid_data[field] = invalid_value

    with pytest.raises(ValidationError) as error:
        FoodCreate(**invalid_data)

    assert error_message in str(error)

def test_valid_dailylog():
    valid_dailylog = DailyLogCreate(user_id=1)

    assert valid_dailylog.model_dump() == {
        "user_id":1
    }

def test_invalid_dailylog():
    invalid_data = {"user_id":-1}
    
    with pytest.raises(ValidationError) as error:
        DailyLogCreate(**invalid_data)

    assert "Input should be greater than 0" in str(error)

def test_valid_foodentry():
    valid_foodentry = FoodEntryCreate(daily_log_id=1, food_id=1, quantity=1)

    assert valid_foodentry.model_dump() == {
        "daily_log_id":1,
        "food_id":1,
        "quantity":1.0
    }

@pytest.mark.parametrize("field,invalid_value,error_message", [
    ("daily_log_id", "-1", "Input should be greater than 0"),
    ("food_id", "-1", "Input should be greater than 0"),
    ("quantity", "-1", "Input should be greater than 0"),
])
def test_invalid_foodentry(field, invalid_value, error_message):
    valid_data = {
        "daily_log_id":1,
        "food_id":1,
        "quantity":1.0
    }
    invalid_data = valid_data.copy()
    invalid_data[field] = invalid_value

    with pytest.raises(ValidationError) as error:
        FoodEntryCreate(**invalid_data)

    assert error_message in str(error)