from PySide6.QtWidgets import QApplication
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Engine

from src.db.init_db import check_database_connection, initialize_database
from src.fetch.athlete_fetch import AthleteFilterParams
from src.repo.athlete_repo import AthletePayload
from src.services.service_factory import ServiceFactory
from src.view.athlete_dialog import AthleteDialog
from src.view.delete_dialog import DeleteDialog
from src.view.main_window import MainWindow
from src.view.search_dialog import SearchDialog


class AppController:
    def __init__(self, app: QApplication, engine: Engine, service_factory: ServiceFactory):
        self.app = app
        self.engine = engine
        self.service_factory = service_factory
        self.athlete_service = service_factory.create_athlete_service()
        self.ingest_service = service_factory.create_ingest_service()
        self.window = MainWindow(self)
        self.page = 1
        self.page_size = 10
        self.is_tree_mode = False

    def start(self) -> int:
        try:
            check_database_connection(self.engine)
            initialize_database(self.engine)
        except Exception as error:
            self.window.show_error("Ошибка подключения к PostgreSQL", str(error))
            return 1

        self.reload_from_database()
        self.window.show()
        return self.app.exec()

    def reload_from_database(self) -> None:
        try:
            items, total = self.athlete_service.fetch_page(
                page=self.page,
                page_size=self.page_size,
            )
            max_page = max(1, ((total - 1) // self.page_size) + 1) if total else 1
            if self.page > max_page:
                self.page = max_page
                items, total = self.athlete_service.fetch_page(
                    page=self.page,
                    page_size=self.page_size,
                )
            self.window.set_table_data(items, total, self.page, self.page_size)
        except SQLAlchemyError as error:
            self.window.show_error("Ошибка загрузки данных", str(error))

    def flush_current_state_to_database(self) -> None:
        self.reload_from_database()
        self.window.show_info(
            "Сохранение в БД",
            "Все текущие изменения уже сохранены в PostgreSQL.",
        )

    def on_page_changed(self, page: int) -> None:
        self.page = page
        self.reload_from_database()

    def on_page_size_changed(self, page_size: int) -> None:
        self.page_size = page_size
        self.page = 1
        self.reload_from_database()

    def toggle_view_mode(self) -> None:
        self.is_tree_mode = not self.is_tree_mode
        if self.is_tree_mode:
            self.window.switch_to_tree()
        else:
            self.window.switch_to_table()

    def open_add_dialog(self) -> None:
        dialog = AthleteDialog(self.window)
        if dialog.exec():
            payload = dialog.get_payload()
            self.add_athlete(payload)

    def add_athlete(self, payload: AthletePayload) -> None:
        try:
            self.athlete_service.add_athlete(payload)
            self.reload_from_database()
            self.window.show_info("Добавление", "Запись успешно добавлена.")
        except SQLAlchemyError as error:
            self.window.show_error("Ошибка добавления", str(error))

    def open_search_dialog(self) -> None:
        dialog = SearchDialog(self, self.window)
        dialog.exec()

    def open_delete_dialog(self) -> None:
        dialog = DeleteDialog(self, self.window)
        if dialog.exec():
            self.reload_from_database()

    def search_athletes(
        self,
        params: AthleteFilterParams,
        page: int,
        page_size: int,
    ) -> tuple[list, int]:
        return self.athlete_service.fetch_page(page, page_size, params)

    def delete_athletes_by_filters(self, params: AthleteFilterParams) -> int:
        try:
            deleted = self.athlete_service.delete_athletes_by_filters(params)
            self.reload_from_database()
            return deleted
        except SQLAlchemyError as error:
            self.window.show_error("Ошибка удаления", str(error))
            return 0

    def get_distinct_filter_values(self) -> tuple[list[str], list[str]]:
        try:
            return self.athlete_service.get_distinct_filter_values()
        except SQLAlchemyError as error:
            self.window.show_error("Ошибка загрузки фильтров", str(error))
            return [], []

    def import_from_xml(self, file_path: str) -> None:
        try:
            imported_count = self.ingest_service.import_xml_to_db(file_path)
            self.reload_from_database()
            self.window.show_info("Импорт XML", f"Импортировано записей: {imported_count}")
        except Exception as error:
            self.window.show_error("Ошибка импорта XML", str(error))

    def export_to_xml(self, file_path: str) -> None:
        try:
            exported_count = self.ingest_service.export_db_to_xml(file_path)
            self.window.show_info("Экспорт XML", f"Экспортировано записей: {exported_count}")
        except Exception as error:
            self.window.show_error("Ошибка экспорта XML", str(error))
