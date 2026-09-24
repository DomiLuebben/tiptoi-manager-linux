"""
Product detail dialog modal.
Displays full cover, description, metadata, and allows direct download to pen.
"""

import os
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextBrowser, QProgressBar, QMessageBox, QWidget
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ..api import TiptoiAPI
from ..pen import PenInfo

class DownloadThread(QThread):
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, api: TiptoiAPI, url: str, dest_path: str):
        super().__init__()
        self.api = api
        self.url = url
        self.dest_path = dest_path
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            ok = self.api.download_file(
                self.url,
                self.dest_path,
                on_progress=lambda cur, tot: self.progress.emit(cur, tot),
                cancel_check=lambda: self._cancelled,
            )
            if ok:
                self.finished.emit(True, "Erfolgreich heruntergeladen!")
            else:
                self.finished.emit(False, "Download abgebrochen.")
        except Exception as e:
            self.finished.emit(False, str(e))


class ProductDetailDialog(QDialog):
    product_installed = pyqtSignal(str)  # Emits product id

    def __init__(
        self, 
        product: Dict[str, Any], 
        api: TiptoiAPI, 
        pen: Optional[PenInfo], 
        assets_dir: str, 
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.product = product
        self.api = api
        self.pen = pen
        self.assets_dir = assets_dir
        self.download_thread: Optional[DownloadThread] = None

        self.setWindowTitle(product.get("name", "tiptoi® Produkt"))
        self.setFixedSize(650, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # Left Column: Cover Image
        left_layout = QVBoxLayout()
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(220, 310)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        """)

        # Find best image
        images = self.product.get("images", [])
        img_url = ""
        for tag in ["detail", "thumb", "search"]:
            for img in images:
                if tag in img.get("tags", []):
                    img_url = img.get("url", "")
                    break
            if img_url:
                break
        if not img_url and images:
            img_url = images[0].get("url", "")

        if img_url:
            cached_path = self.api.get_cached_image_path(img_url)
            if cached_path and os.path.exists(cached_path):
                pixmap = QPixmap(cached_path).scaled(
                    210, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                self.cover_label.setPixmap(pixmap)
            else:
                self.cover_label.setText("Lade Bild…")
        else:
            self.cover_label.setText("Kein Bild")

        left_layout.addWidget(self.cover_label)
        left_layout.addStretch()
        main_layout.addLayout(left_layout)

        # Right Column: Details & Action
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # Series (e.g. "Wieso? Weshalb? Warum?")
        series = self.product.get("series", "")
        if series:
            series_label = QLabel(series.upper())
            series_label.setStyleSheet("color: #dc971f; font-weight: bold; font-size: 12px;")
            right_layout.addWidget(series_label)

        # Product Title
        name_label = QLabel(self.product.get("name", ""))
        name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #231914;")
        name_label.setWordWrap(True)
        right_layout.addWidget(name_label)

        # Metadata badges: Age, Categories, ID
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(8)

        age_from = self.product.get("ageFrom", 0)
        age_to = self.product.get("ageTo", 0)
        if age_from or age_to:
            age_badge = QLabel(f"Alter: {age_from}-{age_to} Jahre")
            age_badge.setStyleSheet("""
                background-color: #e9ecef;
                color: #495057;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            """)
            meta_layout.addWidget(age_badge)

        pid = self.product.get("id", "")
        if pid:
            id_badge = QLabel(f"Art.-Nr. {pid}")
            id_badge.setStyleSheet("""
                background-color: #e9ecef;
                color: #6c757d;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 11px;
            """)
            meta_layout.addWidget(id_badge)

        meta_layout.addStretch()
        right_layout.addLayout(meta_layout)

        # Description
        desc_text = self.product.get("description", "") or self.product.get("shortDescription", "")
        self.desc_browser = QTextBrowser()
        self.desc_browser.setPlainText(desc_text)
        self.desc_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background: transparent;
                color: #55595c;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        right_layout.addWidget(self.desc_browser)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 12px; color: #6c757d;")
        self.status_label.setVisible(False)
        right_layout.addWidget(self.status_label)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.download_btn = QPushButton("Auf den Stift laden")
        self.download_btn.setFixedHeight(40)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #1c57a0;
                color: #ffffff;
                border: none;
                border-radius: 20px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #154580;
            }
            QPushButton:disabled {
                background-color: #b0c4de;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)
        btn_layout.addWidget(self.download_btn)

        close_btn = QPushButton("Schließen")
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f5;
                color: #495057;
                border: 1px solid #ced4da;
                border-radius: 20px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        right_layout.addLayout(btn_layout)
        main_layout.addLayout(right_layout)

        # Check if already installed
        self.check_installed_status()

    def check_installed_status(self):
        if not self.pen:
            self.download_btn.setEnabled(False)
            self.download_btn.setText("Kein Stift angeschlossen")
            self.download_btn.setToolTip("Bitte tiptoi® Stift per USB verbinden")
            return

        game_files = self.product.get("gameFiles", [])
        if not game_files:
            self.download_btn.setEnabled(False)
            self.download_btn.setText("Keine Audiodatei verfügbar")
            return

        target_file = game_files[0].get("fileName", "")
        installed_names = [p.filename.lower() for p in self.pen.installed_products]
        if target_file.lower() in installed_names:
            self.download_btn.setEnabled(False)
            self.download_btn.setText("✓ Bereits auf dem Stift")
            self.download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0fb77b;
                    color: #ffffff;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
        else:
            self.download_btn.setEnabled(True)
            self.download_btn.setText("Auf den Stift laden")

    def start_download(self):
        if not self.pen:
            return

        game_files = self.product.get("gameFiles", [])
        if not game_files:
            return

        gme_info = game_files[0]
        url = gme_info.get("url")
        filename = gme_info.get("fileName")
        if not url or not filename:
            return

        dest_path = os.path.join(self.pen.mount_path, filename)

        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Lade Audiodatei herunter…")
        self.status_label.setVisible(True)

        self.download_thread = DownloadThread(self.api, url, dest_path)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_progress(self, current: int, total: int):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            cur_mb = current / (1024 * 1024)
            tot_mb = total / (1024 * 1024)
            self.status_label.setText(f"Übertrage auf Stift: {cur_mb:.1f} MB / {tot_mb:.1f} MB ({pct}%)")

    def on_download_finished(self, success: bool, message: str):
        self.progress_bar.setVisible(False)
        if success:
            self.status_label.setText("✓ Erfolgreich übertragen!")
            self.status_label.setStyleSheet("font-size: 12px; color: #0fb77b; font-weight: bold;")
            if self.pen:
                self.pen.scan_installed_products()
                self.pen.update_storage_info()
            self.check_installed_status()
            self.product_installed.emit(self.product.get("id", ""))
            QMessageBox.information(
                self, 
                "Fertig", 
                f"Die Audiodatei für '{self.product.get('name')}' wurde erfolgreich auf den tiptoi® Stift übertragen!"
            )
        else:
            self.status_label.setText(f"Fehler: {message}")
            self.status_label.setStyleSheet("font-size: 12px; color: #e02424;")
            self.download_btn.setEnabled(True)
            QMessageBox.critical(self, "Download-Fehler", f"Konnte Datei nicht laden: {message}")
