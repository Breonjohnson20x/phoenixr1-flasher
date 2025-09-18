# gui_app.py
# PhoenixR1 — Rabbit R1 Resurrection Tool

import os
import sys
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QFileDialog, QCheckBox, QMessageBox, QStatusBar, QGroupBox
)
from PySide6.QtGui import QTextCursor, QIcon
from PySide6.QtCore import Qt, Signal, QObject, QPoint, QTimer

import utils
import mtk_wrapper as mtk

APP_TITLE = "🔥 PhoenixR1 — Rabbit R1 Resurrection Tool"
PHOENIX_ORANGE = "#ff7a18"


# --------------------------
# UI helpers (Easter Egg)
# --------------------------
class OneClickButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orig_style = ""
        self.rabbit_label = None

    def enterEvent(self, event):
        # subtle pulse via temporary border color
        self._orig_style = self.styleSheet()
        self.setStyleSheet(self._orig_style + f" QPushButton{{ border: 1px solid {PHOENIX_ORANGE}; }}")
        if self.rabbit_label:
            self.rabbit_label.show_rabbit_hint(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._orig_style)
        if self.rabbit_label:
            self.rabbit_label.hide_rabbit_hint()
        super().leaveEvent(event)


class RabbitHintLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Keep it plain UTF-8 (no escape sequences)
        self.setText("🐇🔥 Phoenix Mode Enabled — careful, legend says the rabbit likes surprises.")
        self.setStyleSheet("QLabel { background: rgba(20,20,20,220); padding: 8px; border-radius: 8px;
