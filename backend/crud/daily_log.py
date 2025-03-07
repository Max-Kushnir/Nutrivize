from .base import CRUD
from backend.models import DailyLog

daily_log_crud = CRUD(model=DailyLog)
