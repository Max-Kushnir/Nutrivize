from .base import CRUD
from nutrition_logger.models import DailyLog

daily_log_crud = CRUD(model=DailyLog)
