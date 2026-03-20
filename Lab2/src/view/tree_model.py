from PySide6.QtGui import QStandardItem, QStandardItemModel

from src.models.athlete import Athlete


class AthleteTreeModel(QStandardItemModel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Запись / Поле", "Значение"])

    def set_athletes(self, athletes: list[Athlete]) -> None:
        self.clear()
        self.setHorizontalHeaderLabels(["Запись / Поле", "Значение"])

        for athlete in athletes:
            root_label = QStandardItem(athlete.full_name)
            root_value = QStandardItem("")

            fields = [
                ("Состав", athlete.squad or "n/a"),
                ("Позиция", athlete.position),
                ("Титулы", str(athlete.titles)),
                ("Вид спорта", athlete.sport),
                ("Разряд", athlete.rank),
            ]

            for key, value in fields:
                key_item = QStandardItem(key)
                value_item = QStandardItem(value)
                root_label.appendRow([key_item, value_item])

            self.appendRow([root_label, root_value])
