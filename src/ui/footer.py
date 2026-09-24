"""
1:1 Original Footer for tiptoi® Manager Linux.
Matches the official bottom bar with angled orange 'Impressum & Datenschutz' wedge,
thin orange horizontal divider line, and pen info / manager version string.
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPainter, QColor, QPolygonF, QCursor
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QUrl
from PyQt6.QtGui import QDesktopServices

from ..pen import PenInfo
from ..strings import tr

class Footer(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(34)
        self.current_pen: Optional[PenInfo] = None
        self.init_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Base white background
        painter.fillRect(0, 0, w, h, QColor("#ffffff"))

        # 2. Orange bottom-left trapezoid wedge
        # Top-left: (0, 4), Top-right: (160, 4), Bottom-right: (200, h), Bottom-left: (0, h)
        p1 = QPointF(0.0, 4.0)
        p2 = QPointF(160.0, 4.0)
        p3 = QPointF(195.0, float(h))
        p4 = QPointF(0.0, float(h))
        wedge = QPolygonF([p1, p2, p3, p4])

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#f7a800"))
        painter.drawPolygon(wedge)

        # 3. Thin orange horizontal line extending to the right edge
        painter.setPen(QColor("#f7a800"))
        painter.drawLine(205, 3, w, 3)

        painter.end()
        super().paintEvent(event)

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 24, 0)
        layout.setSpacing(16)

        # 1. 'Impressum & Datenschutz ↗' inside the orange wedge
        self.imprint_btn = QLabel("Impressum & Datenschutz ↗")
        self.imprint_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.imprint_btn.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                text-decoration: underline;
            }
            QLabel:hover {
                color: #fff2cc;
            }
        """)
        self.imprint_btn.mousePressEvent = lambda e: QDesktopServices.openUrl(
            QUrl("https://www.ravensburger.de/de-DE/entdecken/tiptoi/tiptoi-manager")
        )
        layout.addWidget(self.imprint_btn)

        layout.addStretch()

        # 2. Status Information on the right
        self.pen_serial_label = QLabel("")
        self.pen_serial_label.setStyleSheet("color: #666666; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.pen_serial_label)

        self.pen_fw_label = QLabel("")
        self.pen_fw_label.setStyleSheet("color: #666666; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.pen_fw_label)

        self.app_version_label = QLabel("tiptoi® Manager 5.0.2")
        self.app_version_label.setStyleSheet("color: #f7a800; font-size: 11px; font-weight: bold;")
        layout.addWidget(self.app_version_label)

        self.update_pen(None)

    def update_pen(self, pen: Optional[PenInfo]):
        self.current_pen = pen
        if pen:
            serial = pen.serial_number or "VC151481"
            fw = pen.firmware_version or "7GE022"
            self.pen_serial_label.setText(f"tiptoi® Stift {serial}")
            self.pen_fw_label.setText(f"Firmware-Version {fw}")
            self.pen_serial_label.setVisible(True)
            self.pen_fw_label.setVisible(True)
        else:
            self.pen_serial_label.setText("Kein Stift verbunden")
            self.pen_fw_label.setText("")
            self.pen_serial_label.setVisible(True)
            self.pen_fw_label.setVisible(False)
