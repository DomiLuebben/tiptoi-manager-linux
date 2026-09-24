"""
Main Window for tiptoi® Manager Linux.
Integrates 1:1 Original Header, Left Sidebar with Arch.png swoosh and standing 3D pen,
Vertical Navigation Buttons, Stacked Content Screens, and 1:1 Footer.
"""

import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStackedWidget, QMessageBox, QFrame
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

from ..api import TiptoiAPI
from ..pen import PenDetector, PenInfo
from ..strings import tr

from .header import Header
from .footer import Footer
from .nav_button import NavButton
from .download_screen import DownloadScreen
from .catalog_screen import CatalogScreen
from .pen_screen import PenScreen
from .help_screen import HelpScreen
from .product_detail_dialog import ProductDetailDialog

class CatalogLoaderThread(QThread):
    loaded = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, api: TiptoiAPI):
        super().__init__()
        self.api = api

    def run(self):
        try:
            catalog = self.api.get_catalog()
            self.loaded.emit(catalog)
        except Exception as e:
            self.error.emit(str(e))


class LeftSidebar(QWidget):
    """
    Left sidebar rendering the iconic Arch.png yellow/orange curved swoop
    behind the navigation buttons, and hosting the standing upright 3D pen graphic.
    """
    def __init__(self, assets_dir: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.assets_dir = assets_dir
        arch_path = os.path.join(assets_dir, "Arch.png")
        self.arch_pixmap = QPixmap(arch_path) if os.path.exists(arch_path) else QPixmap()
        self.setFixedWidth(375)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # White base background
        painter.fillRect(self.rect(), QColor("#ffffff"))

        # Draw Arch.png swoop on the left side
        if not self.arch_pixmap.isNull():
            h = self.height()
            scaled_w = int(self.arch_pixmap.width() * (h / self.arch_pixmap.height()))
            scaled_arch = self.arch_pixmap.scaled(
                scaled_w, h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(-45, 0, scaled_arch)

        painter.end()
        super().paintEvent(event)


class MainWindow(QMainWindow):
    def __init__(self, base_dir: str):
        super().__init__()
        self.base_dir = base_dir
        self.assets_dir = os.path.join(base_dir, "assets")
        self.api = TiptoiAPI(locale="de-DE")
        self.current_pen: Optional[PenInfo] = None
        self.catalog_data: Dict[str, Any] = {}
        self.nav_buttons = []

        self.setWindowTitle("tiptoi® Manager")
        self.resize(1024, 640)
        self.setMinimumSize(980, 620)

        # Set Window Icon
        icon_path = os.path.join(self.assets_dir, "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

        # Start periodic pen detector timer
        self.pen_timer = QTimer(self)
        self.pen_timer.timeout.connect(self.check_pen_connection)
        self.pen_timer.start(2500)

        # Automatically detect connected pen or simulate mock pen for immediate testing
        self.check_pen_connection()

        # Start catalog loading thread
        self.load_catalog()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #ffffff;")
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Top Header (Bright orange + white logo + status capsule)
        self.header = Header(self.assets_dir, self)
        self.header.pen_selected.connect(self.on_pen_selected)
        self.header.pen_ejected.connect(self.on_pen_ejected)
        self.header.request_simulate.connect(self.simulate_pen)
        self.main_layout.addWidget(self.header)

        # 2. Main Middle Area (Sidebar + Content Area)
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # --- LEFT SIDEBAR ---
        self.sidebar = LeftSidebar(self.assets_dir, self)
        sidebar_h_layout = QHBoxLayout(self.sidebar)
        sidebar_h_layout.setContentsMargins(12, 20, 8, 20)
        sidebar_h_layout.setSpacing(6)

        # Left Column inside Sidebar: Vertical Navigation Buttons
        nav_col = QVBoxLayout()
        nav_col.setSpacing(14)
        nav_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Nav Button 0: Audiodateien laden (Purple)
        btn0 = NavButton(
            0, "Audiodateien", "laden",
            os.path.join(self.assets_dir, "nav_download_hi.png"),
            os.path.join(self.assets_dir, "nav_download_selected.png"),
            "#8d5494", self
        )
        btn0.clicked.connect(self.on_nav_clicked)
        nav_col.addWidget(btn0)
        self.nav_buttons.append(btn0)

        # Nav Button 1: Produktkatalog ansehen (Teal)
        btn1 = NavButton(
            1, "Produktkatalog", "ansehen",
            os.path.join(self.assets_dir, "nav_catalog_hi.png"),
            os.path.join(self.assets_dir, "nav_catalog_selected.png"),
            "#36a88b", self
        )
        btn1.clicked.connect(self.on_nav_clicked)
        nav_col.addWidget(btn1)
        self.nav_buttons.append(btn1)

        # Nav Button 2: Stift und Inhalte verwalten (Orange)
        btn2 = NavButton(
            2, "Stift und Inhalte", "verwalten",
            os.path.join(self.assets_dir, "nav_pen_hi.png"),
            os.path.join(self.assets_dir, "nav_pen_selected.png"),
            "#f7a800", self
        )
        btn2.clicked.connect(self.on_nav_clicked)
        nav_col.addWidget(btn2)
        self.nav_buttons.append(btn2)

        # Nav Button 3: Hilfe und Informationen (Blue)
        btn3 = NavButton(
            3, "Hilfe und", "Informationen",
            os.path.join(self.assets_dir, "nav_help_hi.png"),
            os.path.join(self.assets_dir, "nav_help_selected.png"),
            "#4fa2b8", self
        )
        btn3.clicked.connect(self.on_nav_clicked)
        nav_col.addWidget(btn3)
        self.nav_buttons.append(btn3)

        nav_col.addStretch()
        sidebar_h_layout.addLayout(nav_col)

        # Right Column inside Sidebar: Standing Upright 3D Pen Illustration
        self.pen_standing_label = QLabel()
        self.pen_standing_label.setFixedWidth(125)
        self.pen_standing_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.pen_standing_label.setStyleSheet("background: transparent; border: none; margin-top: 6px;")
        self.update_standing_pen_graphic()
        sidebar_h_layout.addWidget(self.pen_standing_label)

        body_layout.addWidget(self.sidebar)

        # --- RIGHT CONTENT AREA ---
        self.screen_stack = QStackedWidget()
        self.screen_stack.setStyleSheet("background-color: #ffffff;")

        # Screen 0: Download Screen
        self.download_screen = DownloadScreen(self.api, self.assets_dir)
        self.download_screen.open_product_detail.connect(self.show_product_detail)
        self.screen_stack.addWidget(self.download_screen)

        # Screen 1: Catalog Screen
        self.catalog_screen = CatalogScreen(self.api, self.assets_dir)
        self.catalog_screen.open_product_detail.connect(self.show_product_detail)
        self.screen_stack.addWidget(self.catalog_screen)

        # Screen 2: Pen Screen ("Dateien auf Ihrem Stift")
        self.pen_screen = PenScreen(self.api, self.assets_dir)
        self.pen_screen.pen_updated.connect(lambda: self.header.set_pen(self.current_pen))
        self.screen_stack.addWidget(self.pen_screen)

        # Screen 3: Help Screen
        self.help_screen = HelpScreen(self.assets_dir)
        self.screen_stack.addWidget(self.help_screen)

        body_layout.addWidget(self.screen_stack, 1)
        self.main_layout.addWidget(body_widget, 1)

        # 3. Bottom Footer
        self.footer = Footer(self)
        self.main_layout.addWidget(self.footer)

        # Select tab 2 ("Stift und Inhalte verwalten") by default (matching the user's screenshot!)
        self.on_nav_clicked(2)

    def update_standing_pen_graphic(self):
        pen_sprite = "PenFullRev14@2x.png"
        if self.current_pen and self.current_pen.full_pen_sprite_name:
            pen_sprite = f"{self.current_pen.full_pen_sprite_name}.png"

        pen_path = os.path.join(self.assets_dir, pen_sprite)
        if not os.path.exists(pen_path):
            pen_path = os.path.join(self.assets_dir, "PenFullRev14@2x.png")

        if os.path.exists(pen_path):
            pix = QPixmap(pen_path).scaled(
                125, 440,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.pen_standing_label.setPixmap(pix)

    def on_nav_clicked(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.set_selected(i == index)
        self.screen_stack.setCurrentIndex(index)
        if index == 2 and self.pen_screen:
            self.pen_screen.refresh_display()

    def load_catalog(self):
        self.catalog_loader = CatalogLoaderThread(self.api)
        self.catalog_loader.loaded.connect(self.on_catalog_loaded)
        self.catalog_loader.error.connect(self.on_catalog_error)
        self.catalog_loader.start()

    def on_catalog_loaded(self, catalog: Dict[str, Any]):
        self.catalog_data = catalog
        self.download_screen.set_catalog(catalog)
        self.catalog_screen.set_catalog(catalog)
        self.pen_screen.set_catalog(catalog)

    def on_catalog_error(self, err_msg: str):
        pass

    def check_pen_connection(self):
        # Don't override simulated pen unless physical pen found
        if self.current_pen and self.current_pen.mount_path.endswith("mock_pen"):
            if os.path.exists(self.current_pen.mount_path):
                return

        pen = PenDetector.find_connected_pen()
        if pen and not self.current_pen:
            self.on_pen_selected(pen)
        elif not pen and self.current_pen and not self.current_pen.mount_path.endswith("mock_pen"):
            self.on_pen_ejected()
        elif not self.current_pen:
            # Check if mock_pen exists
            mock_dir = os.path.join(self.base_dir, "mock_pen")
            if os.path.exists(mock_dir):
                mock_pen = PenDetector.scan_path_for_pen(mock_dir)
                if mock_pen:
                    self.on_pen_selected(mock_pen)

    def on_pen_selected(self, pen: PenInfo):
        self.current_pen = pen
        self.header.set_pen(pen)
        self.footer.update_pen(pen)
        self.download_screen.set_pen(pen)
        self.pen_screen.set_pen(pen)
        self.update_standing_pen_graphic()

    def on_pen_ejected(self):
        self.current_pen = None
        self.header.set_pen(None)
        self.footer.update_pen(None)
        self.download_screen.set_pen(None)
        self.pen_screen.set_pen(None)
        self.update_standing_pen_graphic()

    def simulate_pen(self):
        mock_dir = os.path.join(self.base_dir, "mock_pen")
        pen = PenDetector.create_simulated_pen(mock_dir, generation="REV4")
        self.on_pen_selected(pen)
        QMessageBox.information(
            self,
            "Test-Stift aktiviert",
            f"Ein simulierter tiptoi® Stift (REV4) wurde im Test-Ordner erstellt:\n{mock_dir}\n\n"
            "Sie können jetzt Audiodateien direkt herunterladen und testen!"
        )

    def show_product_detail(self, product: Dict[str, Any]):
        dialog = ProductDetailDialog(
            product, self.api, self.current_pen, self.assets_dir, self
        )
        dialog.product_installed.connect(lambda _: self.header.set_pen(self.current_pen))
        dialog.exec()
