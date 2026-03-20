from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from src.controller.app_controller import AppController
from src.core.settings import load_settings
from src.db.engine import create_db_engine
from src.db.session import create_session_factory, create_session_scope_factory
from src.services.service_factory import ServiceFactory


def main() -> int:
    app = QApplication(sys.argv)
    try:
        settings = load_settings(Path(".env"))
        engine = create_db_engine(settings)
        session_factory = create_session_factory(engine)
        session_scope_factory = create_session_scope_factory(session_factory)
        service_factory = ServiceFactory(session_scope_factory)
        controller = AppController(app, engine, service_factory)
    except Exception as error:
        QMessageBox.critical(None, "Ошибка инициализации", str(error))
        return 1

    return controller.start()


if __name__ == "__main__":
    raise SystemExit(main())
