from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
)

from src.fetch.athlete_fetch import AthleteFilterParams
from src.view.filter_panel import AthleteFilterPanel
from src.view.pagination_widget import PaginationWidget
from src.view.table_models import AthleteTableModel


class SearchDialog(QDialog):
    def __init__(self, controller, parent=None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.page = 1
        self.page_size = 10
        self.current_params = AthleteFilterParams()
        self.setWindowTitle("Поиск спортсменов")
        self.resize(900, 600)
        self._build_ui()
        self.reload_dynamic_values()
        self.run_search()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.filter_panel = AthleteFilterPanel(self)
        self.table_model = AthleteTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)

        controls_layout = QHBoxLayout()
        self.search_button = QPushButton("Найти")
        self.close_button = QPushButton("Закрыть")
        controls_layout.addWidget(self.search_button)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.close_button)

        self.pagination = PaginationWidget(self)

        layout.addWidget(self.filter_panel)
        layout.addWidget(self.table_view)
        layout.addWidget(self.pagination)
        layout.addLayout(controls_layout)

        self.search_button.clicked.connect(self._on_search_clicked)
        self.close_button.clicked.connect(self.reject)
        self.pagination.page_changed.connect(self._on_page_changed)
        self.pagination.page_size_changed.connect(self._on_page_size_changed)

    def reload_dynamic_values(self) -> None:
        sports, ranks = self.controller.get_distinct_filter_values()
        self.filter_panel.set_dynamic_values(sports, ranks)

    def _validate(self) -> bool:
        params = self.filter_panel.to_filter_params()
        if params.use_titles_range and params.titles_min > params.titles_max:
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Минимум титулов не может быть больше максимума.",
            )
            return False
        if params.use_name_or_sport and not params.name_or_sport_value.strip():
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Заполните значение для фильтра ФИО/вид спорта.",
            )
            return False
        if params.use_name_or_rank and not params.name_or_rank_value.strip():
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Заполните значение для фильтра ФИО/разряд.",
            )
            return False
        self.current_params = params
        return True

    def _on_search_clicked(self) -> None:
        if not self._validate():
            return
        self.page = 1
        self.run_search()

    def _on_page_changed(self, page: int) -> None:
        self.page = page
        self.run_search()

    def _on_page_size_changed(self, page_size: int) -> None:
        self.page_size = page_size
        self.page = 1
        self.run_search()

    def run_search(self) -> None:
        if self.page != 1 and not self._validate():
            return
        items, total = self.controller.search_athletes(
            params=self.current_params,
            page=self.page,
            page_size=self.page_size,
        )
        self.table_model.set_athletes(items)
        self.pagination.set_state(self.page, self.page_size, total, len(items))
        self.table_view.resizeColumnsToContents()
