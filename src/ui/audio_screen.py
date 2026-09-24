"""
Audio Screen ("Hörbücher und Lieder").
Browse audio products, songs, and audiobooks.
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..api import TiptoiAPI
from ..strings import tr
from .download_screen import ProductCard

class AudioScreen(QWidget):
    open_product_detail = pyqtSignal(dict)

    def __init__(self, api: TiptoiAPI, assets_dir: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = api
        self.assets_dir = assets_dir
        self.audio_products: List[Dict[str, Any]] = []
        self.init_ui()

    def set_catalog(self, catalog: Dict[str, Any]):
        self.audio_products = catalog.get("audios", [])
        self.render_grid()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 20, 32, 20)
        main_layout.setSpacing(16)

        title = QLabel(tr("navigationbar_audiobooks", "Hörbücher und Lieder"))
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #231914;")
        main_layout.addWidget(title)

        self.count_label = QLabel()
        self.count_label.setStyleSheet("font-size: 13px; color: #6c757d;")
        main_layout.addWidget(self.count_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.grid_container)
        main_layout.addWidget(scroll)

    def render_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.count_label.setText(f"{len(self.audio_products)} Titel verfügbar")

        col = 0
        row = 0
        for prod in self.audio_products[:40]:
            card = ProductCard(prod, self.api)
            card.clicked.connect(self.open_product_detail.emit)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1
