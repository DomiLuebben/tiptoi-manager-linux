"""
Custom Navigation Button matching the 1:1 original tiptoi Manager design.
Horizontal pill with rounded caps, custom circular icon, and 2-line title.
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal

class NavButton(QFrame):
    clicked = pyqtSignal(int)

    def __init__(
        self,
        index: int,
        title_line1: str,
        title_line2: str,
        normal_icon_path: str,
        selected_icon_path: str,
        text_color: str,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.index = index
        self.title_line1 = title_line1
        self.title_line2 = title_line2
        self.normal_icon_path = normal_icon_path
        self.selected_icon_path = selected_icon_path
        self.text_color = text_color
        self._is_selected = False

        self.setFixedHeight(54)
        self.setFixedWidth(230)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 3, 14, 3)
        layout.setSpacing(10)

        # 1. Circular Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(46, 46)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.icon_label)

        # 2. Two-line Text Label
        text_combined = f"{self.title_line1}\n{self.title_line2}" if self.title_line2 else self.title_line1
        self.text_label = QLabel(text_combined)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.text_label)
        layout.addStretch()

        self.update_style()

    def set_selected(self, selected: bool):
        self._is_selected = selected
        self.update_style()

    def update_style(self):
        icon_path = self.selected_icon_path if self._is_selected else self.normal_icon_path
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(46, 46, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pix)

        if self._is_selected:
            # Highlighted orange pill (exact match to screenshot)
            self.setStyleSheet("""
                QFrame {
                    background-color: #f7a800;
                    border: 2px solid #ffffff;
                    border-radius: 27px;
                }
            """)
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 13px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                    line-height: 1.1;
                }
            """)
        else:
            # White pill matching screenshot
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: #ffffff;
                    border: 2px solid #ffffff;
                    border-radius: 27px;
                }}
                QFrame:hover {{
                    background-color: #fffaf0;
                    border: 2px solid #f7a800;
                }}
            """)
            self.text_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.text_color};
                    font-size: 13px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                    line-height: 1.1;
                }}
            """)

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
