from .base import CRUD
from backend.models.food import Food

food_crud = CRUD(model=Food)
