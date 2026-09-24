"""
Help and Information Screen ("Hilfe und Informationen").
Features quick help guides, tiptoi pen connection tutorial, and FAQs.
"""

import os
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton
)
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import Qt, QUrl

from ..strings import tr

class HelpScreen(QWidget):
    def __init__(self, assets_dir: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.assets_dir = assets_dir
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 10)
        main_layout.setSpacing(10)

        # 1. Title
        title_label = QLabel("Hilfe und Informationen")
        title_label.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 19px;
                font-weight: 500;
                background: transparent;
            }
        """)
        main_layout.addWidget(title_label)

        # 2. Orange underline
        underline = QFrame()
        underline.setFrameShape(QFrame.Shape.HLine)
        underline.setFixedHeight(2)
        underline.setStyleSheet("background-color: #f7a800; border: none;")
        main_layout.addWidget(underline)

        # 3. Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(16)

        # Tutorial card
        tut_frame = QFrame()
        tut_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        tut_layout = QVBoxLayout(tut_frame)

        tut_title = QLabel("So verbinden Sie Ihren tiptoi® Stift:")
        tut_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #231914;")
        tut_layout.addWidget(tut_title)

        steps = [
            "1. Schalten Sie Ihren tiptoi® Stift ein (Einschalttaste drücken, bis die Melodie ertönt).",
            "2. Schließen Sie das mitgelieferte USB-Kabel an den Stift und an Ihren Computer an.",
            "3. Der Stift wird unter Linux automatisch als Wechselspeicher eingebunden und oben rechts als 'verbunden' angezeigt.",
            "4. Wählen Sie im Reiter 'Audiodateien laden' das gewünschte Produkt aus und klicken Sie auf 'Laden'."
        ]
        for s in steps:
            lbl = QLabel(s)
            lbl.setStyleSheet("color: #495057; font-size: 12px; margin-top: 4px;")
            lbl.setWordWrap(True)
            tut_layout.addWidget(lbl)

        layout.addWidget(tut_frame)

        # Linux support note
        linux_frame = QFrame()
        linux_frame.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        linux_layout = QVBoxLayout(linux_frame)
        linux_title = QLabel("Linux-Kompatibilitätshinweis")
        linux_title.setStyleSheet("color: #166534; font-weight: bold; font-size: 13px;")
        linux_layout.addWidget(linux_title)

        linux_desc = QLabel(
            "Diese Version des tiptoi® Managers läuft nativ unter Linux ohne Wine oder Virtualisierung. "
            "Das FAT16/FAT32 Dateisystem des Stifts wird direkt über Standard-Linux-Systemaufrufe verwaltet. "
            "Vor dem Abziehen des Kabels bitte immer die Auswerfen-Taste ⏏ drücken, damit alle Audiodaten sicher geschrieben werden."
        )
        linux_desc.setStyleSheet("color: #15803d; font-size: 11px;")
        linux_desc.setWordWrap(True)
        linux_layout.addWidget(linux_desc)
        layout.addWidget(linux_frame)

        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
