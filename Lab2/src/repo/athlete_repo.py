from dataclasses import dataclass
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.fetch.athlete_fetch import AthleteFetchService, AthleteFilterParams
from src.models.athlete import Athlete


@dataclass(slots=True)
class AthletePayload:
    full_name: str
    squad: Optional[str]
    position: str
    titles: int
    sport: str
    rank: str


class AthleteRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, payload: AthletePayload) -> Athlete:
        athlete = Athlete(
            full_name=payload.full_name,
            squad=payload.squad,
            position=payload.position,
            titles=payload.titles,
            sport=payload.sport,
            rank=payload.rank,
        )
        self.session.add(athlete)
        self.session.flush()
        return athlete

    def add_many(self, payloads: list[AthletePayload]) -> list[Athlete]:
        athletes = [
            Athlete(
                full_name=payload.full_name,
                squad=payload.squad,
                position=payload.position,
                titles=payload.titles,
                sport=payload.sport,
                rank=payload.rank,
            )
            for payload in payloads
        ]
        self.session.add_all(athletes)
        self.session.flush()
        return athletes

    def get(self, athlete_id: int) -> Optional[Athlete]:
        return self.session.get(Athlete, athlete_id)

    def list_all(self) -> list[Athlete]:
        return list(
            self.session.scalars(
                select(Athlete).order_by(Athlete.full_name.asc(), Athlete.id.asc())
            )
        )

    def delete_by_id(self, athlete_id: int) -> bool:
        athlete = self.get(athlete_id)
        if athlete is None:
            return False
        self.session.delete(athlete)
        self.session.flush()
        return True

    def delete_by_filters(
        self,
        fetch_service: AthleteFetchService,
        params: AthleteFilterParams,
    ) -> int:
        statement = delete(Athlete)
        for expression in fetch_service.build_filters(params):
            statement = statement.where(expression)
        result = self.session.execute(statement)
        self.session.flush()
        return result.rowcount or 0

    def replace_all(self, payloads: list[AthletePayload]) -> int:
        self.session.execute(delete(Athlete))
        self.add_many(payloads)
        self.session.flush()
        return len(payloads)
