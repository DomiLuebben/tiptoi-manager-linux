"""
1:1 Original Header for tiptoi® Manager Linux.
Matches the official bright orange top bar with diagonal white stripe,
white tiptoi logo, 'Ihr Stift' capsule, and 'Optionen / Anmelden' card.
"""

import os
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QFrame, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QPolygonF, QFont
from PyQt6.QtCore import Qt, QPointF, pyqtSignal

from ..pen import PenInfo, PenDetector
from ..strings import tr

class Header(QWidget):
    pen_selected = pyqtSignal(object)  # Emits PenInfo
    pen_ejected = pyqtSignal()
    request_simulate = pyqtSignal()
    open_settings = pyqtSignal()

    def __init__(self, assets_dir: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.assets_dir = assets_dir
        self.current_pen: Optional[PenInfo] = None
        self.setFixedHeight(86)
        self.init_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Base orange background
        painter.fillRect(self.rect(), QColor("#f7a800"))

        # 2. Slanted white stripe behind/next to the logo (exact 1:1 match)
        stripe_width = 18.0
        # Bottom start around x=145, top around x=260
        p1 = QPointF(145.0, float(self.height()))
        p2 = QPointF(145.0 + stripe_width, float(self.height()))
        p3 = QPointF(265.0 + stripe_width, 0.0)
        p4 = QPointF(265.0, 0.0)
        
        polygon = QPolygonF([p1, p2, p3, p4])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#ffffff"))
        painter.drawPolygon(polygon)

        painter.end()
        super().paintEvent(event)

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 8, 16, 8)
        main_layout.setSpacing(16)

        # 1. White tiptoi Logo with "Spiel dich schlau"
        self.logo_label = QLabel()
        logo_path = os.path.join(self.assets_dir, "logo_de.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("<b>tiptoi®</b>")
            self.logo_label.setStyleSheet("font-size: 26px; color: #ffffff;")
        self.logo_label.setStyleSheet("background: transparent; border: none;")
        main_layout.addWidget(self.logo_label)

        main_layout.addStretch()

        # 2. White "Ihr Stift" Capsule Box (exact match to screenshot)
        self.pen_card = QFrame()
        self.pen_card.setObjectName("penCard")
        self.pen_card.setFixedSize(210, 68)
        self.pen_card.setStyleSheet("""
            QFrame#penCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        pen_card_layout = QHBoxLayout(self.pen_card)
        pen_card_layout.setContentsMargins(10, 4, 8, 4)
        pen_card_layout.setSpacing(8)

        # Status text column
        p_text_layout = QVBoxLayout()
        p_text_layout.setSpacing(3)
        p_text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.pen_title_label = QLabel("Ihr Stift")
        self.pen_title_label.setStyleSheet("font-size: 11px; color: #508da4; font-weight: bold; background: transparent; border: none;")
        p_text_layout.addWidget(self.pen_title_label)

        # Pills: "verbunden" (teal) and "X.XX GB frei" (yellow-orange)
        self.conn_pill = QLabel("nicht verbunden")
        self.conn_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.conn_pill.setFixedHeight(18)
        self.conn_pill.setStyleSheet("""
            background-color: #8c949d;
            color: #ffffff;
            border-radius: 9px;
            padding: 1px 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        p_text_layout.addWidget(self.conn_pill)

        self.space_pill = QLabel("0 GB frei")
        self.space_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.space_pill.setFixedHeight(18)
        self.space_pill.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f7a800, stop:1 #fcd34d);
            color: #ffffff;
            border-radius: 9px;
            padding: 1px 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        self.space_pill.setVisible(False)
        p_text_layout.addWidget(self.space_pill)

        pen_card_layout.addLayout(p_text_layout)

        # Mini Pen icon + eject button overlay on the right inside capsule
        pen_img_container = QWidget()
        pen_img_container.setFixedSize(54, 60)
        pen_img_layout = QHBoxLayout(pen_img_container)
        pen_img_layout.setContentsMargins(0, 0, 0, 0)
        pen_img_layout.setSpacing(0)

        self.pen_thumb_label = QLabel()
        self.pen_thumb_label.setFixedSize(32, 56)
        self.pen_thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pen_thumb_label.setStyleSheet("background: transparent; border: none;")
        pen_img_layout.addWidget(self.pen_thumb_label)

        self.eject_btn = QPushButton("⏏")
        self.eject_btn.setToolTip("Stift sicher trennen")
        self.eject_btn.setFixedSize(20, 20)
        self.eject_btn.setStyleSheet("""
            QPushButton {
                background-color: #f7a800;
                color: #ffffff;
                border: 1px solid #ffffff;
                border-radius: 10px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d98200;
            }
        """)
        self.eject_btn.clicked.connect(self.on_eject_clicked)
        self.eject_btn.setVisible(False)
        pen_img_layout.addWidget(self.eject_btn)

        pen_card_layout.addWidget(pen_img_container)
        main_layout.addWidget(self.pen_card)

        # 3. Top-Right "Optionen / Anmelden" Card Box (exact match to screenshot)
        menu_card = QFrame()
        menu_card.setObjectName("menuCard")
        menu_card.setFixedSize(115, 68)
        menu_card.setStyleSheet("""
            QFrame#menuCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        menu_layout = QVBoxLayout(menu_card)
        menu_layout.setContentsMargins(6, 4, 6, 4)
        menu_layout.setSpacing(2)
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Row 1: Optionen (Clickable button with drop-down menu)
        self.options_btn = QPushButton("≡  Optionen")
        self.options_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.options_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #358eb2;
                border: none;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
                padding: 4px 6px;
            }
            QPushButton:hover {
                color: #1b6282;
                background-color: #f0f7fa;
                border-radius: 4px;
            }
        """)
        self.options_btn.clicked.connect(self.show_options_menu)
        menu_layout.addWidget(self.options_btn)

        # Row 2: Anmelden
        self.login_btn = QPushButton("👤  Anmelden")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #358eb2;
                border: none;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
                padding: 4px 6px;
            }
            QPushButton:hover {
                color: #1b6282;
                background-color: #f0f7fa;
                border-radius: 4px;
            }
        """)
        self.login_btn.clicked.connect(self.on_login_clicked)
        menu_layout.addWidget(self.login_btn)

        main_layout.addWidget(menu_card)
        self.update_pen_display()

    def show_options_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                padding: 4px;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f7a800;
                color: #ffffff;
            }
        """)

        sim_action = menu.addAction("🧪 Test-Stift simulieren")
        sim_action.triggered.connect(self.request_simulate.emit)

        choose_action = menu.addAction("📁 Stift-Ordner manuell wählen…")
        choose_action.triggered.connect(self.choose_pen_directory)

        menu.addSeparator()
        info_action = menu.addAction("ℹ Über tiptoi® Manager Linux")
        info_action.triggered.connect(self.show_about)

        # Popup under options button
        menu.exec(self.options_btn.mapToGlobal(self.options_btn.rect().bottomLeft()))

    def show_about(self):
        QMessageBox.about(
            self,
            "Über tiptoi® Manager Linux",
            "<h3>tiptoi® Manager für Linux</h3>"
            "<b>Version 5.0.2</b> (Nativer Linux-Port)<br><br>"
            "Dies ist eine <b>1:1 Kopie / Nachbildung</b> des offiziellen tiptoi® Managers für Linux-Systeme.<br><br>"
            "<b>Rechtlicher Hinweis / Urheberrecht:</b><br>"
            "Sämtliche Bild-, Ton- und Grafik-Assets (Logos, Icons, Stiftmodelle, Produktkatalog) "
            "sowie die Marken <i>tiptoi®</i> und <i>Ravensburger</i> sind geistiges Eigentum und "
            "<b>Copyright der Ravensburger Verlag GmbH</b>.<br><br>"
            "Inoffizielles Community-Projekt für native Linux-Kompatibilität ohne Wine."
        )

    def on_login_clicked(self):
        QMessageBox.information(
            self,
            "Ravensburger Konto",
            "Ein Login ist für den tiptoi® Manager unter Linux nicht erforderlich.\n"
            "Alle Audiodateien und der Katalog werden direkt über die offiziellen CDN-Server geladen."
        )

    def choose_pen_directory(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "tiptoi® Stift-Verzeichnis wählen",
            os.path.expanduser("~")
        )
        if path:
            pen = PenDetector.scan_path_for_pen(path)
            if pen:
                self.pen_selected.emit(pen)
            else:
                reply = QMessageBox.question(
                    self,
                    "Kein Stift erkannt",
                    f"Im gewählten Verzeichnis wurde keine tiptoi® Kennung gefunden:\n{path}\n\n"
                    "Möchten Sie dieses Verzeichnis als tiptoi® Stift initialisieren?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    pen = PenDetector.create_simulated_pen(path, generation="REV4")
                    self.pen_selected.emit(pen)

    def update_pen_display(self):
        pen = self.current_pen
        if pen:
            self.pen_title_label.setText("Ihr Stift")
            self.conn_pill.setText("verbunden")
            self.conn_pill.setStyleSheet("""
                background-color: #38b2ac;
                color: #ffffff;
                border-radius: 9px;
                padding: 1px 8px;
                font-size: 10px;
                font-weight: bold;
            """)
            free_gb = pen.free_space / (1024 * 1024 * 1024)
            self.space_pill.setText(f"{free_gb:.2f} GB frei")
            self.space_pill.setVisible(True)

            # Mini pen icon tilted
            icon_path = os.path.join(self.assets_dir, "PenDisconnect.png")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(self.assets_dir, f"{pen.pen_sprite_name}.png")
            if os.path.exists(icon_path):
                pix = QPixmap(icon_path).scaled(30, 52, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.pen_thumb_label.setPixmap(pix)
            self.eject_btn.setVisible(True)
        else:
            self.pen_title_label.setText("Ihr Stift")
            self.conn_pill.setText("nicht verbunden")
            self.conn_pill.setStyleSheet("""
                background-color: #8c949d;
                color: #ffffff;
                border-radius: 9px;
                padding: 1px 8px;
                font-size: 10px;
                font-weight: bold;
            """)
            self.space_pill.setVisible(False)
            icon_path = os.path.join(self.assets_dir, "PenDisconnect.png")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(self.assets_dir, "PenGen2@2x.png")
            if os.path.exists(icon_path):
                pix = QPixmap(icon_path).scaled(30, 52, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.pen_thumb_label.setPixmap(pix)
            self.eject_btn.setVisible(False)

    def set_pen(self, pen: Optional[PenInfo]):
        self.current_pen = pen
        self.update_pen_display()

    def on_eject_clicked(self):
        if self.current_pen:
            success, msg = self.current_pen.eject()
            if success:
                self.pen_ejected.emit()
            else:
                QMessageBox.warning(self, "Trennen fehlgeschlagen", f"Stift konnte nicht getrennt werden:\n{msg}")
