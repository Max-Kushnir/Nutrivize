from .base import CRUD
from api.models import DailyLog

daily_log_crud = CRUD(model=DailyLog)
