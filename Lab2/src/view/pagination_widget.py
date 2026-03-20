from math import ceil

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


class PaginationWidget(QWidget):
    page_changed = Signal(int)
    page_size_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._page = 1
        self._page_size = 10
        self._total_items = 0
        self._page_items = 0
        self._build_ui()
        self._connect_signals()
        self._update_label()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.first_button = QPushButton("Первая")
        self.prev_button = QPushButton("Пред")
        self.next_button = QPushButton("След")
        self.last_button = QPushButton("Последняя")
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["5", "10", "20", "50"])
        self.page_size_combo.setCurrentText("10")
        self.info_label = QLabel()

        layout.addWidget(self.first_button)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.last_button)
        layout.addWidget(QLabel("Размер страницы:"))
        layout.addWidget(self.page_size_combo)
        layout.addStretch(1)
        layout.addWidget(self.info_label)

    def _connect_signals(self) -> None:
        self.first_button.clicked.connect(self.go_first)
        self.prev_button.clicked.connect(self.go_previous)
        self.next_button.clicked.connect(self.go_next)
        self.last_button.clicked.connect(self.go_last)
        self.page_size_combo.currentTextChanged.connect(self._on_page_size_changed)

    def set_state(self, page: int, page_size: int, total_items: int, page_items: int) -> None:
        self._page = max(page, 1)
        self._page_size = max(page_size, 1)
        self._total_items = max(total_items, 0)
        self._page_items = max(page_items, 0)
        self._update_label()

    def total_pages(self) -> int:
        return max(1, ceil(self._total_items / self._page_size)) if self._page_size else 1

    def go_first(self) -> None:
        self.page_changed.emit(1)

    def go_previous(self) -> None:
        self.page_changed.emit(max(1, self._page - 1))

    def go_next(self) -> None:
        self.page_changed.emit(min(self.total_pages(), self._page + 1))

    def go_last(self) -> None:
        self.page_changed.emit(self.total_pages())

    def _on_page_size_changed(self, value: str) -> None:
        self.page_size_changed.emit(int(value))

    def _update_label(self) -> None:
        total_pages = self.total_pages()
        self.info_label.setText(
            f"Стр. {self._page} из {total_pages}; показано {self._page_items} из {self._total_items}"
        )
