from __future__ import annotations
from typing import List, TYPE_CHECKING
import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrition_logger.database.db import Base

if TYPE_CHECKING:
    from .user import User
    from .food_entry import FoodEntry

class DailyLog(Base):
    __tablename__ = 'daily_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, default=datetime.date.today)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    user: Mapped[User] = relationship(back_populates="logs")
    food_entries: Mapped[List[FoodEntry]] = relationship(back_populates="daily_log", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('user_id', 'date', name='_user_date_uc'),)

    
