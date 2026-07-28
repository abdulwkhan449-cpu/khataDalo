#!/usr/bin/env python3
"""
Khata Dalo — Desktop Ledger & POS
Entry point: initializes the database, applies the theme, and launches the
main window. Run with:  python main.py
"""

import sys
import os

# Make sure local package imports (db, ui, utils) resolve regardless of CWD.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from db import init_db, backup_database
from ui.main_window import MainWindow


def main():
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("Khata Dalo")
    app.setOrganizationName("Khata Dalo")

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    # End-of-day auto-backup: run once at startup if no backup exists for today.
    try:
        from datetime import date
        from db import BACKUP_DIR
        today_tag = date.today().isoformat()
        already_done = os.path.isdir(BACKUP_DIR) and any(today_tag in f for f in os.listdir(BACKUP_DIR))
        if not already_done:
            backup_database()
    except Exception:
        pass  # never block app startup on backup failure

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
