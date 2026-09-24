"""
1:1 Product Card Component matching the official tiptoi Manager design.
Square card with crisp orange border, inner horizontal orange divider, and orange title box.
"""

import os
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal

from ..api import TiptoiAPI

class OriginalProductCard(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, product: Dict[str, Any], api: TiptoiAPI, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.product = product
        self.api = api
        self.setFixedSize(130, 126)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Outer orange container frame
        self.box_frame = QFrame()
        self.box_frame.setFixedSize(130, 126)
        self.box_frame.setStyleSheet("""
            QFrame#cardBox {
                background-color: #ffffff;
                border: 2px solid #f7a800;
                border-radius: 4px;
            }
            QFrame#cardBox:hover {
                border: 2.5px solid #d98200;
                background-color: #fffdf9;
            }
        """)
        self.box_frame.setObjectName("cardBox")

        box_layout = QVBoxLayout(self.box_frame)
        box_layout.setContentsMargins(2, 2, 2, 2)
        box_layout.setSpacing(0)

        # 1. Top Section: Product Cover Image
        self.img_container = QWidget()
        self.img_container.setFixedHeight(88)
        img_layout = QVBoxLayout(self.img_container)
        img_layout.setContentsMargins(2, 2, 2, 2)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet("border: none; background: transparent;")

        # Find best image url
        img_url = ""
        for img in self.product.get("images", []):
            if "thumb" in img.get("tags", []) or "search" in img.get("tags", []):
                img_url = img.get("url", "")
                break
        if not img_url and self.product.get("images"):
            img_url = self.product["images"][0].get("url", "")

        if img_url:
            cached = self.api.get_cached_image_path(img_url)
            if cached and os.path.exists(cached):
                pix = QPixmap(cached).scaled(
                    120, 82, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                self.img_label.setPixmap(pix)
            else:
                self.img_label.setText("tiptoi®")
                self.img_label.setStyleSheet("color: #f7a800; font-weight: bold; font-size: 13px; border: none;")
        else:
            self.img_label.setText("tiptoi®")
            self.img_label.setStyleSheet("color: #f7a800; font-weight: bold; font-size: 13px; border: none;")

        img_layout.addWidget(self.img_label)
        box_layout.addWidget(self.img_container)

        # 2. Orange Divider Line
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setFixedHeight(2)
        self.divider.setStyleSheet("background-color: #f7a800; border: none; margin: 0px;")
        box_layout.addWidget(self.divider)

        # 3. Bottom Section: Product Title
        raw_title = self.product.get("name", "")
        # Clean title to match original screenshot
        display_title = raw_title.replace("tiptoi®", "").strip()
        self.title_label = QLabel(display_title)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #e68a00;
                font-size: 9.5px;
                font-weight: bold;
                border: none;
                background-color: #ffffff;
                padding: 1px 2px;
                line-height: 1.05;
            }
        """)
        self.title_label.setFixedHeight(28)
        box_layout.addWidget(self.title_label)

        main_layout.addWidget(self.box_frame)

    def mousePressEvent(self, event):
        self.clicked.emit(self.product)
