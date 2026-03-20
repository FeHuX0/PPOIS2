from pathlib import Path
from xml.dom.minidom import Document

from src.models.athlete import Athlete


class AthleteXmlDomWriter:
    def write(self, athletes: list[Athlete], output_path: str | Path) -> None:
        document = Document()
        root = document.createElement("athletes")
        document.appendChild(root)

        for athlete in athletes:
            athlete_node = document.createElement("athlete")
            root.appendChild(athlete_node)

            self._append_text_node(document, athlete_node, "full_name", athlete.full_name)
            self._append_text_node(document, athlete_node, "squad", athlete.squad or "n/a")
            self._append_text_node(document, athlete_node, "position", athlete.position)
            self._append_text_node(document, athlete_node, "titles", str(athlete.titles))
            self._append_text_node(document, athlete_node, "sport", athlete.sport)
            self._append_text_node(document, athlete_node, "rank", athlete.rank)

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as file:
            file.write(document.toprettyxml(indent="  ", encoding=None))

    @staticmethod
    def _append_text_node(
        document: Document,
        parent,
        node_name: str,
        value: str,
    ) -> None:
        node = document.createElement(node_name)
        node.appendChild(document.createTextNode(value))
        parent.appendChild(node)
