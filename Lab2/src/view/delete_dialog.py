from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.view.filter_panel import AthleteFilterPanel


class DeleteDialog(QDialog):
    def __init__(self, controller, parent=None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Удаление спортсменов")
        self.resize(520, 320)
        self._build_ui()
        self.reload_dynamic_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.filter_panel = AthleteFilterPanel(self)

        controls_layout = QHBoxLayout()
        self.delete_button = QPushButton("Удалить")
        self.close_button = QPushButton("Закрыть")
        controls_layout.addWidget(self.delete_button)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.close_button)

        layout.addWidget(self.filter_panel)
        layout.addLayout(controls_layout)

        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.close_button.clicked.connect(self.reject)

    def reload_dynamic_values(self) -> None:
        sports, ranks = self.controller.get_distinct_filter_values()
        self.filter_panel.set_dynamic_values(sports, ranks)

    def _on_delete_clicked(self) -> None:
        params = self.filter_panel.to_filter_params()
        if not (
            params.use_name_or_sport
            or params.use_titles_range
            or params.use_name_or_rank
        ):
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Для удаления нужно включить хотя бы одно условие фильтрации.",
            )
            return
        if params.use_titles_range and params.titles_min > params.titles_max:
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Минимум титулов не может быть больше максимума.",
            )
            return
        if params.use_name_or_sport and not params.name_or_sport_value.strip():
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Заполните значение для фильтра ФИО/вид спорта.",
            )
            return
        if params.use_name_or_rank and not params.name_or_rank_value.strip():
            QMessageBox.warning(
                self,
                "Ошибка валидации",
                "Заполните значение для фильтра ФИО/разряд.",
            )
            return

        deleted = self.controller.delete_athletes_by_filters(params)
        if deleted:
            QMessageBox.information(self, "Удаление завершено", f"Удалено записей: {deleted}")
            self.accept()
        else:
            QMessageBox.information(self, "Удаление завершено", "Ничего не найдено.")
