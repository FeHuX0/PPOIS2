from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from src.models.athlete import Athlete


@dataclass(slots=True)
class AthleteFilterParams:
    use_name_or_sport: bool = False
    name_or_sport_mode: str = "full_name"
    name_or_sport_value: str = ""
    use_titles_range: bool = False
    titles_min: int = 0
    titles_max: int = 0
    use_name_or_rank: bool = False
    name_or_rank_mode: str = "full_name"
    name_or_rank_value: str = ""


class AthleteFetchService:
    def build_filters(self, params: AthleteFilterParams) -> list:
        filters = []

        if params.use_name_or_sport and params.name_or_sport_value.strip():
            value = params.name_or_sport_value.strip()
            if params.name_or_sport_mode == "sport":
                filters.append(Athlete.sport == value)
            else:
                filters.append(Athlete.full_name.ilike(f"%{value}%"))

        if params.use_titles_range:
            filters.append(Athlete.titles >= params.titles_min)
            filters.append(Athlete.titles <= params.titles_max)

        if params.use_name_or_rank and params.name_or_rank_value.strip():
            value = params.name_or_rank_value.strip()
            if params.name_or_rank_mode == "rank":
                filters.append(Athlete.rank == value)
            else:
                filters.append(Athlete.full_name.ilike(f"%{value}%"))

        return filters

    def build_statement(self, params: Optional[AthleteFilterParams] = None) -> Select[tuple[Athlete]]:
        statement = select(Athlete).order_by(Athlete.full_name.asc(), Athlete.id.asc())
        if params is None:
            return statement
        for expression in self.build_filters(params):
            statement = statement.where(expression)
        return statement

    def fetch_page(
        self,
        session: Session,
        page: int,
        page_size: int,
        params: Optional[AthleteFilterParams] = None,
    ) -> tuple[list[Athlete], int]:
        page = max(page, 1)
        page_size = max(page_size, 1)
        statement = self.build_statement(params)

        count_statement = select(func.count()).select_from(statement.subquery())
        total = session.scalar(count_statement) or 0

        items = list(
            session.scalars(
                statement.limit(page_size).offset((page - 1) * page_size)
            )
        )
        return items, total

    def fetch_all(
        self,
        session: Session,
        params: Optional[AthleteFilterParams] = None,
    ) -> list[Athlete]:
        return list(session.scalars(self.build_statement(params)))

    def distinct_sports(self, session: Session) -> list[str]:
        statement = (
            select(Athlete.sport)
            .where(Athlete.sport.is_not(None))
            .distinct()
            .order_by(Athlete.sport.asc())
        )
        return [value for value in session.scalars(statement) if value]

    def distinct_ranks(self, session: Session) -> list[str]:
        statement = (
            select(Athlete.rank)
            .where(Athlete.rank.is_not(None))
            .distinct()
            .order_by(Athlete.rank.asc())
        )
        return [value for value in session.scalars(statement) if value]
