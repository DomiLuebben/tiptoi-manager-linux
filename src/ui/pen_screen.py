"""
Pen Screen ("Stift und Inhalte verwalten" / "Dateien auf Ihrem Stift").
Matches the 1:1 original layout: Title with orange underline, and 4-column product grid
of installed .gme files with click-to-manage dialog.
"""

import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QGridLayout, QFrame, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from ..pen import PenInfo, InstalledProduct
from ..api import TiptoiAPI
from .product_card import OriginalProductCard
from .product_detail_dialog import ProductDetailDialog

class PenScreen(QWidget):
    pen_updated = pyqtSignal()
    open_product_detail = pyqtSignal(dict)

    def __init__(self, api: TiptoiAPI, assets_dir: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = api
        self.assets_dir = assets_dir
        self.current_pen: Optional[PenInfo] = None
        self.catalog_data: Dict[str, Any] = {}
        self.catalog_by_gme_id: Dict[int, Dict[str, Any]] = {}
        self.catalog_by_filename: Dict[str, Dict[str, Any]] = {}
        self.init_ui()

    def set_catalog(self, catalog: Dict[str, Any]):
        self.catalog_data = catalog
        self.catalog_by_gme_id.clear()
        self.catalog_by_filename.clear()
        for prod in catalog.get("products", []):
            for gf in prod.get("gameFiles", []):
                gid = gf.get("id")
                try:
                    if gid is not None:
                        self.catalog_by_gme_id[int(gid)] = prod
                except Exception:
                    pass
                fn = gf.get("fileName", "").lower()
                if fn:
                    self.catalog_by_filename[fn] = prod
        self.refresh_display()

    def set_pen(self, pen: Optional[PenInfo]):
        self.current_pen = pen
        self.refresh_display()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 16, 20, 10)
        self.main_layout.setSpacing(10)

        # 1. Section Title
        self.title_label = QLabel("Dateien auf Ihrem Stift")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 19px;
                font-weight: 500;
                background: transparent;
            }
        """)
        self.main_layout.addWidget(self.title_label)

        # 2. Orange Underline spanning the full width (exact 1:1 match)
        self.underline = QFrame()
        self.underline.setFrameShape(QFrame.Shape.HLine)
        self.underline.setFixedHeight(2)
        self.underline.setStyleSheet("background-color: #f7a800; border: none;")
        self.main_layout.addWidget(self.underline)

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
        self.main_layout.addWidget(self.scroll_area)

        self.refresh_display()

    def refresh_display(self):
        # Clear existing grid items
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.current_pen:
            empty_lbl = QLabel("Kein tiptoi® Stift verbunden.\nBitte verbinden Sie Ihren Stift über das USB-Kabel.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #888888; font-size: 14px; padding: 40px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0, 1, 4)
            return

        self.current_pen.update_storage_info()
        self.current_pen.scan_installed_products()
        installed_files = self.current_pen.installed_products

        if not installed_files:
            empty_lbl = QLabel("Keine Audiodateien auf dem Stift vorhanden.\nLaden Sie neue Dateien über den Reiter 'Audiodateien laden' herunter.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #888888; font-size: 14px; padding: 40px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0, 1, 4)
            return

        # Display installed products in 4 columns, preserving clean ordering
        def sort_key(item):
            order = [
                'spielfiguren1.gme', 'spielfiguren_reiterhof.gme', 'spielfiguren_pferde.gme', 'turnier_reit-set.gme',
                'wissenquizzen3.gme', 'wissenquizzen2.gme', 'wissenquizzen1.gme', 'wissenquizzenhunde.gme',
                'wissenquizzenmusik.gme', 'spielfiguren3.gme', 'spielfiguren2.gme', 'spielfiguren_dinosaurier.gme'
            ]
            fn = item.filename.lower()
            return order.index(fn) if fn in order else 999

        sorted_files = sorted(installed_files, key=sort_key)
        col_count = 4
        for idx, item in enumerate(sorted_files):
            prod = None
            fn = item.filename.lower()
            if fn in self.catalog_by_filename:
                prod = self.catalog_by_filename[fn]
            elif item.gme_id and item.gme_id in self.catalog_by_gme_id:
                prod = self.catalog_by_gme_id[item.gme_id]

            if not prod:
                # Fallback synthesized product representation
                prod = {
                    "id": item.gme_id or idx,
                    "name": item.product_name or item.filename,
                    "images": [],
                    "gameFiles": [{"fileName": item.filename, "size": item.file_size, "version": item.version}]
                }

            card = OriginalProductCard(prod, self.api, self)
            card.clicked.connect(self.on_card_clicked)
            row = idx // col_count
            col = idx % col_count
            self.grid_layout.addWidget(card, row, col)

    def on_card_clicked(self, product: Dict[str, Any]):
        dialog = ProductDetailDialog(
            product, self.api, self.current_pen, self.assets_dir, self
        )
        dialog.product_installed.connect(self.on_product_modified)
        dialog.exec()

    def on_product_modified(self, _):
        self.refresh_display()
        self.pen_updated.emit()
