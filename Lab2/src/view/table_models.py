from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from src.models.athlete import Athlete


HEADERS = ["ФИО", "Состав", "Позиция", "Титулы", "Вид спорта", "Разряд"]


class AthleteTableModel(QAbstractTableModel):
    def __init__(self, athletes: Optional[list[Athlete]] = None, parent=None) -> None:
        super().__init__(parent)
        self._athletes = athletes or []

    def set_athletes(self, athletes: list[Athlete]) -> None:
        self.beginResetModel()
        self._athletes = athletes
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._athletes)

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(HEADERS)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        athlete = self._athletes[index.row()]
        values = [
            athlete.full_name,
            athlete.squad or "n/a",
            athlete.position,
            athlete.titles,
            athlete.sport,
            athlete.rank,
        ]
        return values[index.column()]

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return HEADERS[section]
        return section + 1
