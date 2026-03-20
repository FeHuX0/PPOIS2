from typing import Callable, Optional

from sqlalchemy.orm import Session

from src.fetch.athlete_fetch import AthleteFetchService, AthleteFilterParams
from src.models.athlete import Athlete
from src.repo.athlete_repo import AthletePayload, AthleteRepository
from src.services.types import SessionScopeFactoryType


RepositoryFactory = Callable[[Session], AthleteRepository]


class AthleteService:
    def __init__(
        self,
        session_scope_factory: SessionScopeFactoryType,
        fetch_service: Optional[AthleteFetchService] = None,
        repository_factory: Optional[RepositoryFactory] = None,
    ) -> None:
        self._session_scope_factory = session_scope_factory
        self._fetch_service = fetch_service or AthleteFetchService()
        self._repository_factory = repository_factory or AthleteRepository

    def fetch_page(
        self,
        page: int,
        page_size: int,
        params: Optional[AthleteFilterParams] = None,
    ) -> tuple[list[Athlete], int]:
        with self._session_scope_factory() as session:
            return self._fetch_service.fetch_page(session, page, page_size, params)

    def add_athlete(self, payload: AthletePayload) -> Athlete:
        with self._session_scope_factory() as session:
            repository = self._repository_factory(session)
            return repository.add(payload)

    def delete_athletes_by_filters(self, params: AthleteFilterParams) -> int:
        with self._session_scope_factory() as session:
            repository = self._repository_factory(session)
            return repository.delete_by_filters(self._fetch_service, params)

    def get_distinct_filter_values(self) -> tuple[list[str], list[str]]:
        with self._session_scope_factory() as session:
            sports = self._fetch_service.distinct_sports(session)
            ranks = self._fetch_service.distinct_ranks(session)
        return sports, ranks
