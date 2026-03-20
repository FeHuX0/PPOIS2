from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QTableView,
    QToolBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.view.pagination_widget import PaginationWidget
from src.view.table_models import AthleteTableModel
from src.view.tree_model import AthleteTreeModel


class MainWindow(QMainWindow):
    def __init__(self, controller, parent=None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Спортсмены")
        self.resize(1100, 700)
        self._build_ui()
        self._create_actions()
        self._create_menu()
        self._create_toolbar()

    def _build_ui(self) -> None:
        self.table_model = AthleteTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)

        self.tree_model = AthleteTreeModel()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)

        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.table_view)
        self.content_stack.addWidget(self.tree_view)

        self.pagination = PaginationWidget(self)
        self.pagination.page_changed.connect(self.controller.on_page_changed)
        self.pagination.page_size_changed.connect(self.controller.on_page_size_changed)

        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.content_stack)
        layout.addWidget(self.pagination)

        self.status_label = QLabel("Готово")
        self.statusBar().addPermanentWidget(self.status_label)

    def _create_actions(self) -> None:
        self.add_action = QAction("Добавить", self)
        self.search_action = QAction("Поиск", self)
        self.delete_action = QAction("Удаление по условиям", self)
        self.load_xml_action = QAction("Загрузить из XML", self)
        self.save_xml_action = QAction("Сохранить в XML", self)
        self.load_db_action = QAction("Загрузить из БД", self)
        self.save_db_action = QAction("Сохранить в БД", self)
        self.toggle_view_action = QAction("Таблица / Дерево", self)
        self.exit_action = QAction("Выход", self)

        self.add_action.triggered.connect(self.controller.open_add_dialog)
        self.search_action.triggered.connect(self.controller.open_search_dialog)
        self.delete_action.triggered.connect(self.controller.open_delete_dialog)
        self.load_xml_action.triggered.connect(self._select_xml_for_import)
        self.save_xml_action.triggered.connect(self._select_xml_for_export)
        self.load_db_action.triggered.connect(self.controller.reload_from_database)
        self.save_db_action.triggered.connect(self.controller.flush_current_state_to_database)
        self.toggle_view_action.triggered.connect(self.controller.toggle_view_mode)
        self.exit_action.triggered.connect(self.close)

    def _create_menu(self) -> None:
        menu = self.menuBar().addMenu("Файл")
        menu.addAction(self.add_action)
        menu.addAction(self.search_action)
        menu.addAction(self.delete_action)
        menu.addSeparator()
        menu.addAction(self.load_xml_action)
        menu.addAction(self.save_xml_action)
        menu.addAction(self.load_db_action)
        menu.addAction(self.save_db_action)
        menu.addSeparator()
        menu.addAction(self.toggle_view_action)
        menu.addSeparator()
        menu.addAction(self.exit_action)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Основная панель", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(toolbar)

        for action in [
            self.add_action,
            self.search_action,
            self.delete_action,
            self.load_xml_action,
            self.save_xml_action,
            self.load_db_action,
            self.save_db_action,
            self.toggle_view_action,
            self.exit_action,
        ]:
            toolbar.addAction(action)

    def set_table_data(self, athletes: list, total: int, page: int, page_size: int) -> None:
        self.table_model.set_athletes(athletes)
        self.tree_model.set_athletes(athletes)
        self.pagination.set_state(page, page_size, total, len(athletes))
        self.table_view.resizeColumnsToContents()
        self.tree_view.expandAll()

    def switch_to_table(self) -> None:
        self.content_stack.setCurrentWidget(self.table_view)
        self.status_label.setText("Режим: таблица")

    def switch_to_tree(self) -> None:
        self.content_stack.setCurrentWidget(self.tree_view)
        self.status_label.setText("Режим: дерево")

    def _select_xml_for_import(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите XML для импорта",
            "",
            "XML Files (*.xml)",
        )
        if file_path:
            self.controller.import_from_xml(file_path)

    def _select_xml_for_export(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить XML",
            "athletes_export.xml",
            "XML Files (*.xml)",
        )
        if file_path:
            self.controller.export_to_xml(file_path)

    def show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)
