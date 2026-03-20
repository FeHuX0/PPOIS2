from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.fetch.athlete_fetch import AthleteFilterParams


class AthleteFilterPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.name_or_sport_group = QGroupBox("Фильтр: ФИО или вид спорта")
        self.name_or_sport_group.setCheckable(True)
        self.name_or_sport_group.setChecked(False)
        name_or_sport_layout = QVBoxLayout(self.name_or_sport_group)
        name_or_sport_radio_layout = QHBoxLayout()
        self.name_radio = QRadioButton("ФИО")
        self.sport_radio = QRadioButton("Вид спорта")
        self.name_radio.setChecked(True)
        name_or_sport_radio_layout.addWidget(self.name_radio)
        name_or_sport_radio_layout.addWidget(self.sport_radio)
        self.name_or_sport_stack = QStackedWidget()
        self.name_edit = QLineEdit()
        self.sport_combo = QComboBox()
        self.name_or_sport_stack.addWidget(self.name_edit)
        self.name_or_sport_stack.addWidget(self.sport_combo)
        name_or_sport_layout.addLayout(name_or_sport_radio_layout)
        name_or_sport_layout.addWidget(self.name_or_sport_stack)

        self.titles_group = QGroupBox("Фильтр: диапазон титулов")
        self.titles_group.setCheckable(True)
        self.titles_group.setChecked(False)
        titles_layout = QFormLayout(self.titles_group)
        self.titles_min_spin = QSpinBox()
        self.titles_max_spin = QSpinBox()
        self.titles_min_spin.setRange(0, 999)
        self.titles_max_spin.setRange(0, 999)
        self.titles_max_spin.setValue(10)
        titles_layout.addRow("Минимум:", self.titles_min_spin)
        titles_layout.addRow("Максимум:", self.titles_max_spin)

        self.name_or_rank_group = QGroupBox("Фильтр: ФИО или разряд")
        self.name_or_rank_group.setCheckable(True)
        self.name_or_rank_group.setChecked(False)
        name_or_rank_layout = QVBoxLayout(self.name_or_rank_group)
        name_or_rank_radio_layout = QHBoxLayout()
        self.name_second_radio = QRadioButton("ФИО")
        self.rank_radio = QRadioButton("Разряд")
        self.name_second_radio.setChecked(True)
        name_or_rank_radio_layout.addWidget(self.name_second_radio)
        name_or_rank_radio_layout.addWidget(self.rank_radio)
        self.name_or_rank_stack = QStackedWidget()
        self.rank_name_edit = QLineEdit()
        self.rank_combo = QComboBox()
        self.name_or_rank_stack.addWidget(self.rank_name_edit)
        self.name_or_rank_stack.addWidget(self.rank_combo)
        name_or_rank_layout.addLayout(name_or_rank_radio_layout)
        name_or_rank_layout.addWidget(self.name_or_rank_stack)

        layout.addWidget(self.name_or_sport_group)
        layout.addWidget(self.titles_group)
        layout.addWidget(self.name_or_rank_group)

    def _connect_signals(self) -> None:
        self.name_radio.toggled.connect(self._sync_stacks)
        self.sport_radio.toggled.connect(self._sync_stacks)
        self.name_second_radio.toggled.connect(self._sync_stacks)
        self.rank_radio.toggled.connect(self._sync_stacks)
        self._sync_stacks()

    def _sync_stacks(self) -> None:
        self.name_or_sport_stack.setCurrentIndex(1 if self.sport_radio.isChecked() else 0)
        self.name_or_rank_stack.setCurrentIndex(1 if self.rank_radio.isChecked() else 0)

    def set_dynamic_values(self, sports: list[str], ranks: list[str]) -> None:
        self.sport_combo.clear()
        self.sport_combo.addItems(sports)
        self.rank_combo.clear()
        self.rank_combo.addItems(ranks)

    def to_filter_params(self) -> AthleteFilterParams:
        return AthleteFilterParams(
            use_name_or_sport=self.name_or_sport_group.isChecked(),
            name_or_sport_mode="sport" if self.sport_radio.isChecked() else "full_name",
            name_or_sport_value=(
                self.sport_combo.currentText()
                if self.sport_radio.isChecked()
                else self.name_edit.text().strip()
            ),
            use_titles_range=self.titles_group.isChecked(),
            titles_min=self.titles_min_spin.value(),
            titles_max=self.titles_max_spin.value(),
            use_name_or_rank=self.name_or_rank_group.isChecked(),
            name_or_rank_mode="rank" if self.rank_radio.isChecked() else "full_name",
            name_or_rank_value=(
                self.rank_combo.currentText()
                if self.rank_radio.isChecked()
                else self.rank_name_edit.text().strip()
            ),
        )
