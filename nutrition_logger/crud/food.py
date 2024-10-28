from .base import CRUD
from nutrition_logger.models.food import Food

food_crud = CRUD(model=Food)
