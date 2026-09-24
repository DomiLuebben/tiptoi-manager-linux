"""
1:1 Design styling and QSS stylesheets for tiptoi® Manager Linux.
Matches Ravensburger brand colors and original Unity UI aesthetic.
"""

# Brand Colors from reverse engineering
COLOR_BLUE = "#1c57a0"
COLOR_BLUE_HOVER = "#154580"
COLOR_BLUE_PRESSED = "#0e305c"

COLOR_ORANGE = "#dc971f"
COLOR_ORANGE_LIGHT = "#f59c00"
COLOR_ORANGE_HOVER = "#c48315"

COLOR_BG = "#f4f5f7"
COLOR_WHITE = "#ffffff"
COLOR_CARD_BORDER = "#dee2e6"

COLOR_TEXT_PRIMARY = "#231914"
COLOR_TEXT_SECONDARY = "#6c757d"
COLOR_TEXT_MUTED = "#9ba2a9"

COLOR_STATUS_CONNECTED = "#0fb77b"
COLOR_STATUS_DISCONNECTED = "#8c949d"

QSS_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLOR_BG};
}}

QWidget {{
    font-family: "Liberation Sans", "Roboto", "DejaVu Sans", sans-serif;
    color: {COLOR_TEXT_PRIMARY};
}}

/* Top Navigation Bar */
QTabBar::tab {{
    background: transparent;
    color: {COLOR_TEXT_SECONDARY};
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 500;
    border-bottom: 3px solid transparent;
}}

QTabBar::tab:selected {{
    color: {COLOR_BLUE};
    font-weight: bold;
    border-bottom: 3px solid {COLOR_ORANGE};
}}

QTabBar::tab:hover:!selected {{
    color: {COLOR_TEXT_PRIMARY};
    background-color: rgba(0, 0, 0, 0.03);
}}

/* Search Input */
QLineEdit.search-bar {{
    background-color: {COLOR_WHITE};
    border: 1px solid #c9cdd0;
    border-radius: 22px;
    padding: 10px 18px 10px 42px;
    font-size: 15px;
    color: {COLOR_TEXT_PRIMARY};
}}

QLineEdit.search-bar:focus {{
    border: 2px solid {COLOR_BLUE};
    background-color: #ffffff;
}}

/* Buttons */
QPushButton.btn-primary {{
    background-color: {COLOR_BLUE};
    color: #ffffff;
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: bold;
}}

QPushButton.btn-primary:hover {{
    background-color: {COLOR_BLUE_HOVER};
}}

QPushButton.btn-primary:pressed {{
    background-color: {COLOR_BLUE_PRESSED};
}}

QPushButton.btn-primary:disabled {{
    background-color: #b0c4de;
    color: #f0f0f0;
}}

QPushButton.btn-secondary {{
    background-color: transparent;
    color: {COLOR_BLUE};
    border: 1px solid {COLOR_BLUE};
    border-radius: 16px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton.btn-secondary:hover {{
    background-color: rgba(28, 87, 160, 0.08);
}}

QPushButton.btn-danger {{
    background-color: #e02424;
    color: #ffffff;
    border: none;
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: bold;
}}

QPushButton.btn-danger:hover {{
    background-color: #c81e1e;
}}

/* Product Cards */
QFrame.product-card {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_CARD_BORDER};
    border-radius: 10px;
}}

QFrame.product-card:hover {{
    border: 1px solid {COLOR_ORANGE};
    background-color: #fafbfc;
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: #c0c4c8;
    min-height: 30px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: #9ba0a6;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Progress Bar */
QProgressBar {{
    border: 1px solid #d0d4d9;
    border-radius: 6px;
    text-align: center;
    background-color: #e9ecef;
    font-size: 11px;
    font-weight: bold;
}}

QProgressBar::chunk {{
    background-color: {COLOR_ORANGE};
    border-radius: 5px;
}}

/* Tooltips */
QToolTip {{
    background-color: #2b3035;
    color: #ffffff;
    border: none;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
}}
"""
