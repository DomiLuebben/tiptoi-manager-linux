"""
Download Screen ("Audiodateien laden").
Matches the 1:1 original layout: Title with orange underline, search bar,
and 4-column product grid with OriginalProductCard components.
"""

import os
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QFrame, QGridLayout, QPushButton
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from ..api import TiptoiAPI
from ..pen import PenInfo
from .product_card import OriginalProductCard

class DownloadScreen(QWidget):
    open_product_detail = pyqtSignal(dict)

    def __init__(self, api: TiptoiAPI, assets_dir: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = api
        self.assets_dir = assets_dir
        self.current_pen: Optional[PenInfo] = None
        self.all_products: List[Dict[str, Any]] = []
        self.filtered_products: List[Dict[str, Any]] = []
        self.init_ui()

    def set_pen(self, pen: Optional[PenInfo]):
        self.current_pen = pen

    def set_catalog(self, catalog: Dict[str, Any]):
        self.all_products = catalog.get("products", [])
        self.filtered_products = self.all_products
        self.populate_grid()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 10)
        main_layout.setSpacing(10)

        # 1. Header Row: Title & Search Input
        header_row = QHBoxLayout()
        header_row.setSpacing(16)

        title_label = QLabel("Audiodateien laden")
        title_label.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 19px;
                font-weight: 500;
                background: transparent;
            }
        """)
        header_row.addWidget(title_label)

        header_row.addStretch()

        # Search Bar
        search_box = QFrame()
        search_box.setFixedSize(220, 32)
        search_box.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 16px;
            }
            QFrame:focus-within {
                border: 1.5px solid #f7a800;
            }
        """)
        s_layout = QHBoxLayout(search_box)
        s_layout.setContentsMargins(10, 2, 10, 2)
        s_layout.setSpacing(6)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #888888; font-size: 12px; border: none; background: transparent;")
        s_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Titel oder Suchbegriff…")
        self.search_input.setStyleSheet("border: none; background: transparent; font-size: 12px; color: #333333;")
        self.search_input.textChanged.connect(self.on_search_changed)
        s_layout.addWidget(self.search_input)

        header_row.addWidget(search_box)
        main_layout.addLayout(header_row)

        # 2. Orange underline
        underline = QFrame()
        underline.setFrameShape(QFrame.Shape.HLine)
        underline.setFixedHeight(2)
        underline.setStyleSheet("background-color: #f7a800; border: none;")
        main_layout.addWidget(underline)

        # 3. Scrollable Grid Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #f7a800;
                min-height: 24px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #d98200;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 10, 8, 10)
        self.grid_layout.setHorizontalSpacing(14)
        self.grid_layout.setVerticalSpacing(14)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area)

    def on_search_changed(self, text: str):
        query = text.strip().lower()
        if not query:
            self.filtered_products = self.all_products
        else:
            self.filtered_products = [
                p for p in self.all_products
                if query in p.get("name", "").lower()
                or query in p.get("description", "").lower()
                or query in p.get("series", "").lower()
            ]
        self.populate_grid()

    def populate_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.filtered_products:
            lbl = QLabel("Keine passenden tiptoi® Produkte gefunden.")
            lbl.setStyleSheet("color: #888888; font-size: 13px; padding: 40px;")
            self.grid_layout.addWidget(lbl, 0, 0, 1, 4)
            return

        col_count = 4
        # Limit to first 60 for instant snappy rendering
        display_list = self.filtered_products[:60]
        for idx, prod in enumerate(display_list):
            card = OriginalProductCard(prod, self.api, self)
            card.clicked.connect(self.open_product_detail.emit)
            row = idx // col_count
            col = idx % col_count
            self.grid_layout.addWidget(card, row, col)
