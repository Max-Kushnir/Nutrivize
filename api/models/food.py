from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint

from api.database.db import Base

class Food(Base):
    __tablename__ = 'foods'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    manufacturer: Mapped[str] = mapped_column(nullable=False)
    serving_size: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(nullable=False)
    calories: Mapped[float] = mapped_column(nullable=False)
    protein: Mapped[float] = mapped_column(nullable=False)
    carbs: Mapped[float] = mapped_column(nullable=False)
    fat: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
            UniqueConstraint('name', 'manufacturer', name='uq_name_manufacturer'),
        )