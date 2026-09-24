"""
tiptoi® Manager for Linux
Reverse engineered 1:1 replica of Ravensburger tiptoi® Manager.
"""

import sys
import os

# Set base dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

def main():
    # Enable High DPI scaling
    app = QApplication(sys.argv)
    app.setApplicationName("tiptoi® Manager")
    app.setOrganizationName("Ravensburger")

    window = MainWindow(BASE_DIR)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
