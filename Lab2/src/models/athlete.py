from typing import Optional

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Athlete(Base):
    __tablename__ = "athletes"
    __table_args__ = (
        CheckConstraint("titles >= 0", name="ck_athletes_titles_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    squad: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, default="n/a")
    position: Mapped[str] = mapped_column(String(128), nullable=False)
    titles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sport: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    rank: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "squad": self.squad,
            "position": self.position,
            "titles": self.titles,
            "sport": self.sport,
            "rank": self.rank,
        }
