from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from src.repo.athlete_repo import AthletePayload


SPORT_OPTIONS = [
    "Футбол",
    "Баскетбол",
    "Волейбол",
    "Хоккей",
    "Плавание",
    "Лёгкая атлетика",
    "Теннис",
    "Бокс",
]

SQUAD_OPTIONS = ["основной", "запасной", "n/a"]
RANK_OPTIONS = ["1-й юношеский", "2-й разряд", "3й-разряд", "кмс", "мастер спорта"]


class AthleteDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Добавить спортсмена")
        self.resize(420, 260)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.full_name_edit = QLineEdit()
        self.squad_combo = QComboBox()
        self.squad_combo.addItems(SQUAD_OPTIONS)
        self.position_edit = QLineEdit()
        self.titles_spin = QSpinBox()
        self.titles_spin.setRange(0, 999)
        self.sport_combo = QComboBox()
        self.sport_combo.addItems(SPORT_OPTIONS)
        self.rank_combo = QComboBox()
        self.rank_combo.addItems(RANK_OPTIONS)

        form_layout.addRow("ФИО:", self.full_name_edit)
        form_layout.addRow("Состав:", self.squad_combo)
        form_layout.addRow("Позиция:", self.position_edit)
        form_layout.addRow("Титулы:", self.titles_spin)
        form_layout.addRow("Вид спорта:", self.sport_combo)
        form_layout.addRow("Разряд:", self.rank_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(buttons)

    def _validate_and_accept(self) -> None:
        full_name = self.full_name_edit.text().strip()
        position = self.position_edit.text().strip()

        if not full_name:
            QMessageBox.warning(self, "Ошибка валидации", "Поле ФИО не должно быть пустым.")
            return
        if not position:
            QMessageBox.warning(self, "Ошибка валидации", "Поле Позиция не должно быть пустым.")
            return
        if self.titles_spin.value() < 0:
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Количество титулов должно быть неотрицательным.",
            )
            return

        self.accept()

    def get_payload(self) -> AthletePayload:
        return AthletePayload(
            full_name=self.full_name_edit.text().strip(),
            squad=self.squad_combo.currentText(),
            position=self.position_edit.text().strip(),
            titles=self.titles_spin.value(),
            sport=self.sport_combo.currentText(),
            rank=self.rank_combo.currentText(),
        )
