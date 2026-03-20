from src.fetch.athlete_fetch import AthleteFetchService
from src.ingest.xml_dom_writer import AthleteXmlDomWriter
from src.ingest.xml_sax_reader import AthleteXmlSaxReader
from src.services.athlete_service import AthleteService
from src.services.ingest_service import AthleteIngestService
from src.services.types import SessionScopeFactoryType


class ServiceFactory:
    def __init__(self, session_scope_factory: SessionScopeFactoryType) -> None:
        self._session_scope_factory = session_scope_factory
        self._fetch_service = AthleteFetchService()

    def create_athlete_service(self) -> AthleteService:
        return AthleteService(
            session_scope_factory=self._session_scope_factory,
            fetch_service=self._fetch_service,
        )

    def create_ingest_service(self) -> AthleteIngestService:
        return AthleteIngestService(
            session_scope_factory=self._session_scope_factory,
            fetch_service=self._fetch_service,
            xml_writer=AthleteXmlDomWriter(),
            xml_reader=AthleteXmlSaxReader(),
        )
