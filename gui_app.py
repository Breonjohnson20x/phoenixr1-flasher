# gui_app.py
# PhoenixR1 — Rabbit R1 Resurrection Tool

import os
import sys
import threading

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
        self.setText("🐇🔥 Phoenix Mode Enabled — careful, legend says the rabbit likes surprises.")
        self.setStyleSheet("QLabel { background: rgba(20,20,20,220); padding: 8px; border-radius: 8px; font-size: 12px; }")
        self.setVisible(False)

    def show_rabbit_hint(self, anchor_btn: QPushButton):
        if anchor_btn:
            gpos = anchor_btn.mapToGlobal(anchor_btn.rect().topRight())
            parent = self.parent()
            if parent:
                self.move(parent.mapFromGlobal(gpos + QPoint(10, -10)))
        self.setVisible(True)
        QTimer.singleShot(1400, self.hide_rabbit_hint)

    def hide_rabbit_hint(self):
        self.setVisible(False)


# --------------------------
# Log signal bus
# --------------------------
class LogBus(QObject):
    line = Signal(str, str)  # (text, level)


# --------------------------
# Main App
# --------------------------
class PhoenixApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        try:
            self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "assets", "phoenix.ico")))
        except Exception:
            pass

        self.resize(900, 640)
        self.logbus = LogBus()
        self.logbus.line.connect(self._append_line)

        # user-selected firmware folder (None = auto)
        self.fw_dir = None

        # Create Easter-egg label BEFORE UI build
        self.rabbit_hint = RabbitHintLabel(self)

        self._build_ui()
        self._refresh_firmware_state()
        self._refresh_device_state()

    # --------------------------
    # Build UI
    # --------------------------
    def _build_ui(self):
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)

        # Flash tab
        self.flash_tab = QWidget()
        self._build_flash_tab(self.flash_tab)
        tabs.addTab(self.flash_tab, "Flash")

        # Tools tab
        self.tools_tab = QWidget()
        self._build_tools_tab(self.tools_tab)
        tabs.addTab(self.tools_tab, "Tools")

        # Drivers tab
        self.drivers_tab = QWidget()
        self._build_drivers_tab(self.drivers_tab)
        tabs.addTab(self.drivers_tab, "Drivers")

        # Log panel
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("QTextEdit { background: #0f0f10; color: #ddd; font-family: Consolas, Menlo, monospace; }")

        # Status bar
        self.status = QStatusBar()
        self.device_label = QLabel("Device: Unknown")
        self.mode_label = QLabel("")  # shows 3-file or 4-file
        pill_css = (
            "QLabel { background: #1f1f1f; color: #e6e6e6; border: 1px solid #2a2a2a; "
            "border-radius: 10px; padding: 2px 8px; }"
        )
        self.mode_label.setStyleSheet(pill_css)
        self.status.addPermanentWidget(self.mode_label)
        self.status.addPermanentWidget(self.device_label)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(self._toolbar())
        layout.addWidget(self.log)
        layout.addWidget(self.status)
        self.setLayout(layout)

        # Dark theme
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #121212;
                color: #e6e6e6;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background: {PHOENIX_ORANGE};
                color: #000;
                padding: 8px 12px;
            }}
            QTabBar::tab:!selected {{
                background: #1e1e1e;
                padding: 8px 12px;
            }}
            QPushButton {{
                background: #1f1f1f;
                border: 1px solid #2a2a2a;
                padding: 8px 12px;
                border-radius: 8px;
            }}
            QPushButton:disabled {{
                background: #1a1a1a;
                color: #666;
            }}
            QPushButton:hover {{
                border-color: {PHOENIX_ORANGE};
            }}
            QGroupBox {{
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
        """)

    def _toolbar(self):
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self._refresh_all)

        self.btn_oneclick = OneClickButton("🔥 One-Click Restore")
        self.btn_oneclick.clicked.connect(self._one_click_restore)

        self.chk_wipe = QCheckBox("Wipe userdata (optional)")
        self.chk_community = QCheckBox("Community Mode")
        self.chk_community.stateChanged.connect(self._community_toggle)

        self.chk_threefile = QCheckBox("3-file mode (skip vendor)")
        self.chk_threefile.stateChanged.connect(self._refresh_firmware_state)

        roww = QWidget()
        l = QHBoxLayout()
        l.addWidget(self.btn_refresh)
        l.addStretch(1)
        l.addWidget(self.chk_wipe)
        l.addWidget(self.chk_community)
        l.addWidget(self.chk_threefile)
        l.addWidget(self.btn_oneclick)
        roww.setLayout(l)

        # Link Easter-egg to button
        self.btn_oneclick.rabbit_label = self.rabbit_hint

        return roww

    def _build_flash_tab(self, tab):
        lay = QVBoxLayout()

        self.paths = {}

        grp = QGroupBox("Partitions")
        g = QVBoxLayout()

        self.lbl_boot = QLabel("boot.img: missing")
        self.btn_flash_boot = QPushButton("Flash boot.img")
        self.btn_flash_boot.clicked.connect(lambda: self._flash_single("boot", self.paths.get("boot")))

        self.lbl_vbmeta = QLabel("vbmeta.img: missing")
        self.btn_flash_vbmeta = QPushButton("Flash vbmeta.img")
        self.btn_flash_vbmeta.clicked.connect(lambda: self._flash_single("vbmeta", self.paths.get("vbmeta")))

        self.lbl_super = QLabel("super/system.img: missing")
        self.btn_flash_super = QPushButton("Flash super/system.img")
        self.btn_flash_super.clicked.connect(lambda: self._flash_single("super_or_system", self.paths.get("super_or_system")))

        self.lbl_vendor = QLabel("vendor.img: missing")
        self.btn_flash_vendor = QPushButton("Flash vendor.img")
        self.btn_flash_vendor.clicked.connect(lambda: self._flash_single("vendor", self.paths.get("vendor")))

        for w in [
            self.lbl_boot, self.btn_flash_boot,
            self.lbl_vbmeta, self.btn_flash_vbmeta,
            self.lbl_super, self.btn_flash_super,
            self.lbl_vendor, self.btn_flash_vendor,
        ]:
            g.addWidget(w)

        grp.setLayout(g)
        lay.addWidget(grp)

        pick = QPushButton("Choose firmware folder…")
        pick.clicked.connect(self._pick_firmware_dir)
        lay.addWidget(pick)

        tab.setLayout(lay)

    def _build_tools_tab(self, tab):
        lay = QVBoxLayout()

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self._run_tool_reset)

        self.btn_reboot_bl = QPushButton("Reboot to Bootloader")
        self.btn_reboot_bl.clicked.connect(self._run_tool_reboot_bl)

        self.btn_wipe = QPushButton("Wipe userdata (DANGER)")
        self.btn_wipe.clicked.connect(self._run_tool_wipe)

        for w in [self.btn_reset, self.btn_reboot_bl, self.btn_wipe]:
            lay.addWidget(w)

        tab.setLayout(lay)

    def _build_drivers_tab(self, tab):
        lay = QVBoxLayout()

        self.btn_zadig = QPushButton("Open Zadig")
        self.btn_zadig.clicked.connect(self._open_zadig)

        self.btn_devmgmt = QPushButton("Open Device Manager")
        self.btn_devmgmt.clicked.connect(self._open_devmgmt)

        lay.addWidget(self.btn_zadig)
        lay.addWidget(self.btn_devmgmt)
        tab.setLayout(lay)

    # --------------------------
    # Log appender
    # --------------------------
    def _append_line(self, text, level="info"):
        if not hasattr(self, "log"):
            return
        self.log.moveCursor(QTextCursor.End)
        color = "#a0a0a0"
        if level == "ok":
            color = "#44d07a"
        elif level == "err":
            color = "#ff4d4f"
        elif level == "warn":
            color = "#f0ad4e"
        self.log.insertHtml(f'<span style="color:{color}">{text}</span><br/>')
        self.log.moveCursor(QTextCursor.End)

    # --------------------------
    # Actions
    # --------------------------
    def _pick_firmware_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select firmware folder", os.path.dirname(__file__))
        if d:
            self.fw_dir = d
            self._append_line(f"Using firmware folder: {d}", "ok")
        else:
            self._append_line("No folder selected. Falling back to defaults.", "warn")
        self._refresh_firmware_state()

    def _refresh_firmware_state(self):
        self.paths = utils.list_firmware_images(self.fw_dir)

        def mark(lbl, path):
            base = lbl.text().split(":")[0]
            if path and os.path.isfile(path):
                lbl.setText(f"{os.path.basename(path)}: ready ✅")
            else:
                lbl.setText(f"{base}: missing ❌")

        mark(self.lbl_boot, self.paths.get("boot"))
        mark(self.lbl_vbmeta, self.paths.get("vbmeta"))
        mark(self.lbl_super, self.paths.get("super_or_system"))
        mark(self.lbl_vendor, self.paths.get("vendor"))

        # log resolved paths
        self._append_line(f"boot: {self.paths.get('boot')}", "info")
        self._append_line(f"vbmeta: {self.paths.get('vbmeta')}", "info")
        self._append_line(f"super/system: {self.paths.get('super_or_system')}", "info")
        self._append_line(f"vendor: {self.paths.get('vendor')}", "info")

        # enable/disable single flash buttons by availability
        self.btn_flash_boot.setEnabled(bool(self.paths.get("boot")))
        self.btn_flash_vbmeta.setEnabled(bool(self.paths.get("vbmeta")))
        self.btn_flash_super.setEnabled(bool(self.paths.get("super_or_system")))
        self.btn_flash_vendor.setEnabled(bool(self.paths.get("vendor")))

        # 3-file mode readiness
        have_boot  = bool(self.paths.get("boot"))
        have_vbm   = bool(self.paths.get("vbmeta"))
        have_super = bool(self.paths.get("super_or_system"))
        have_vendor = bool(self.paths.get("vendor"))
        skip_vendor = self.chk_threefile.isChecked()

        ready = (have_boot and have_vbm and have_super and (have_vendor or skip_vendor))
        # reflect mode chip
        self.mode_label.setText("3-file" if skip_vendor else "4-file")
        # disable vendor button if skipping
        if skip_vendor:
            self.btn_flash_vendor.setEnabled(False)

        self.btn_oneclick.setEnabled(ready and self._is_device_connected())

    def _refresh_device_state(self):
        connected, detail = mtk.detect_device()
        self.device_label.setText(f"Device: {'Connected' if connected else 'Not Detected'}  |  {detail}")

        gate = connected
        for b in [
            self.btn_flash_boot, self.btn_flash_vbmeta, self.btn_flash_super, self.btn_flash_vendor,
            self.btn_reset, self.btn_reboot_bl, self.btn_wipe
        ]:
            b.setEnabled(bool(b.isEnabled() and gate))

        self.btn_oneclick.setEnabled(self.btn_oneclick.isEnabled() and gate)

    def _is_device_connected(self):
        connected, _ = mtk.detect_device()
        return connected

    def _community_toggle(self, state):
        if state == Qt.Checked:
            QMessageBox.information(
                self,
                "Community Mode",
                "This is community-maintained software.\nUse at your own risk. Make sure you own the device and have the legal right to modify it."
            )

    def _ensure_safe(self):
        if not self._is_device_connected():
            QMessageBox.warning(self, "No device", "No device detected. Connect your Rabbit R1 in the correct mode and try again.")
            return False
        return True

    def _worker(self, generator, done_cb=None):
        log_path = utils.log_filename()
        with open(log_path, "a", encoding="utf-8") as logf:
            for line in generator:
                level = "info"
                low = line.lower()
                if "error" in low or "fail" in low or "denied" in low:
                    level = "err"
                elif "ok" in low or "success" in low or "done" in low:
                    level = "ok"
                self.logbus.line.emit(line, level)
                logf.write(line + "\n")
        self.logbus.line.emit(f"Saved log to {log_path}", "warn")
        if done_cb:
            done_cb()

    def _flash_single(self, key, image
