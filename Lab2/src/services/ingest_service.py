from pathlib import Path
from typing import Callable, Optional

from sqlalchemy.orm import Session

from src.fetch.athlete_fetch import AthleteFetchService
from src.ingest.xml_dom_writer import AthleteXmlDomWriter
from src.ingest.xml_sax_reader import AthleteXmlSaxReader
from src.repo.athlete_repo import AthleteRepository
from src.services.types import SessionScopeFactoryType


RepositoryFactory = Callable[[Session], AthleteRepository]


class AthleteIngestService:
    def __init__(
        self,
        session_scope_factory: SessionScopeFactoryType,
        fetch_service: Optional[AthleteFetchService] = None,
        xml_writer: Optional[AthleteXmlDomWriter] = None,
        xml_reader: Optional[AthleteXmlSaxReader] = None,
        repository_factory: Optional[RepositoryFactory] = None,
    ) -> None:
        self._session_scope_factory = session_scope_factory
        self._fetch_service = fetch_service or AthleteFetchService()
        self._xml_writer = xml_writer or AthleteXmlDomWriter()
        self._xml_reader = xml_reader or AthleteXmlSaxReader()
        self._repository_factory = repository_factory or AthleteRepository

    def import_xml_to_db(self, input_path: str | Path, replace_existing: bool = False) -> int:
        payloads = self._xml_reader.read(input_path)
        with self._session_scope_factory() as session:
            repository = self._repository_factory(session)
            if replace_existing:
                repository.replace_all(payloads)
            else:
                repository.add_many(payloads)
            return len(payloads)

    def export_db_to_xml(self, output_path: str | Path) -> int:
        with self._session_scope_factory() as session:
            athletes = self._fetch_service.fetch_all(session)
        self._xml_writer.write(athletes, output_path)
        return len(athletes)
