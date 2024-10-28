from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrition_logger.database.db import Base

if TYPE_CHECKING:
    from .daily_log import DailyLog

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    logs: Mapped[List[DailyLog]] = relationship(back_populates="user", cascade="all, delete-orphan")
