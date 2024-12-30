from .base import CRUD
from api.models.food import Food

food_crud = CRUD(model=Food)
