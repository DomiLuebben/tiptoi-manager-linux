"""
Catalog Screen ("Produktkatalog ansehen").
Matches the 1:1 original layout: Title with orange underline, category filter,
and 4-column product grid with OriginalProductCard components.
"""

import os
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QScrollArea, QFrame, QGridLayout, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..api import TiptoiAPI
from .product_card import OriginalProductCard

class CatalogScreen(QWidget):
    open_product_detail = pyqtSignal(dict)

    def __init__(self, api: TiptoiAPI, assets_dir: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = api
        self.assets_dir = assets_dir
        self.all_products: List[Dict[str, Any]] = []
        self.filtered_products: List[Dict[str, Any]] = []
        self.init_ui()

    def set_catalog(self, catalog: Dict[str, Any]):
        self.all_products = catalog.get("products", [])
        self.filtered_products = self.all_products

        # Populate categories
        categories = set()
        for p in self.all_products:
            series = p.get("series")
            if series:
                categories.add(series)

        self.category_combo.clear()
        self.category_combo.addItem("Alle Kategorien")
        for cat in sorted(categories):
            self.category_combo.addItem(cat)

        self.populate_grid()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 10)
        main_layout.setSpacing(10)

        # 1. Header Row: Title & Filter
        header_row = QHBoxLayout()
        header_row.setSpacing(16)

        title_label = QLabel("Produktkatalog ansehen")
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

        # Category filter dropdown
        self.category_combo = QComboBox()
        self.category_combo.addItem("Alle Kategorien")
        self.category_combo.setFixedWidth(180)
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 14px;
                padding: 4px 12px;
                font-size: 12px;
                color: #495057;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                selection-background-color: #f7a800;
                selection-color: #ffffff;
                border: 1px solid #ced4da;
            }
        """)
        self.category_combo.currentIndexChanged.connect(self.on_filter_changed)
        header_row.addWidget(self.category_combo)

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

    def on_filter_changed(self):
        cat = self.category_combo.currentText()
        if cat == "Alle Kategorien":
            self.filtered_products = self.all_products
        else:
            self.filtered_products = [p for p in self.all_products if p.get("series") == cat]
        self.populate_grid()

    def populate_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.filtered_products:
            lbl = QLabel("Keine Produkte in dieser Kategorie gefunden.")
            lbl.setStyleSheet("color: #888888; font-size: 13px; padding: 40px;")
            self.grid_layout.addWidget(lbl, 0, 0, 1, 4)
            return

        col_count = 4
        display_list = self.filtered_products[:60]
        for idx, prod in enumerate(display_list):
            card = OriginalProductCard(prod, self.api, self)
            card.clicked.connect(self.open_product_detail.emit)
            row = idx // col_count
            col = idx % col_count
            self.grid_layout.addWidget(card, row, col)
