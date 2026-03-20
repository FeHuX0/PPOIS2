from pathlib import Path
from xml.sax import ContentHandler, make_parser

from src.repo.athlete_repo import AthletePayload


class AthleteSaxHandler(ContentHandler):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[AthletePayload] = []
        self.current_tag = ""
        self.current_data: dict[str, str] = {}
        self.current_text: list[str] = []
        self.in_athlete = False

    def startElement(self, name: str, attrs) -> None:
        if name == "athlete":
            self.in_athlete = True
            self.current_data = {}
        self.current_tag = name
        self.current_text = []

    def characters(self, content: str) -> None:
        if self.current_tag:
            self.current_text.append(content)

    def endElement(self, name: str) -> None:
        value = "".join(self.current_text).strip()
        if self.in_athlete and name != "athlete":
            self.current_data[name] = value

        if name == "athlete":
            self.items.append(
                AthletePayload(
                    full_name=self.current_data.get("full_name", "").strip(),
                    squad=self.current_data.get("squad", "n/a").strip() or "n/a",
                    position=self.current_data.get("position", "").strip(),
                    titles=int(self.current_data.get("titles", "0").strip() or "0"),
                    sport=self.current_data.get("sport", "").strip(),
                    rank=self.current_data.get("rank", "").strip(),
                )
            )
            self.in_athlete = False
            self.current_data = {}

        self.current_tag = ""
        self.current_text = []


class AthleteXmlSaxReader:
    def read(self, input_path: str | Path) -> list[AthletePayload]:
        parser = make_parser()
        handler = AthleteSaxHandler()
        parser.setContentHandler(handler)
        parser.parse(str(input_path))
        return handler.items
