# PhoenixR1 — Rabbit R1 Resurrection Tool 🔥

A GUI-based unbrick & flashing utility for the Rabbit R1. Built with **Python**, **PySide6**, and **mtkclient** (CLI).

> ⚠️ **Big Disclaimer**  
> This tool is for owners repairing their own devices. Flashing firmware can permanently brick hardware and may void warranties.  
> **You are responsible** for ensuring you have the legal right to modify the device and for any data loss or damage.

## ✨ Features
- One‑click flashing of `boot.img`, `vbmeta.img`, `super.img`/`system.img`, and `vendor.img` in sequence
- Auto‑detects images placed in the `firmware/` folder (buttons grey out if missing)
- Color‑coded, live log with **Save‑to‑file** after each run
- Built‑in **Reset**, **Reboot to Bootloader**, and optional **Wipe userdata**
- Driver shortcuts (open **Zadig** + **Device Manager**)

## 📦 Requirements
- Windows 10/11 (PowerShell enabled)
- Python 3.11 (for building)
- **mtkclient** installed/available on PATH (either `mtk` or `python -m mtkclient` will be used)
- **WinUSB** driver for your device (use Zadig to install if needed)

## 👟 Quick Start (Source)
1. Install Python 3.11
2. Open a terminal in this folder
3. Create venv + install deps:
   ```bat
   py -3.11 -m venv venv
   venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Install **mtkclient** (outside this project or in the same venv):
   ```bat
   pip install mtkclient
   ```
5. Put your firmware images into `./firmware/`:
   - `boot.img`
   - `vbmeta.img`
   - **one of**: `super.img` **or** `system.img`
   - `vendor.img`
6. Run the app:
   ```bat
   python gui_app.py
   ```

## 🚀 Build EXE
```bat
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --onefile --noconsole gui_app.py -n PhoenixR1_Flasher --icon assets\phoenix.ico
```
The EXE will be at `dist\PhoenixR1_Flasher.exe`

## 🧰 Notes
- The app prefers the `mtk` command if found on PATH; otherwise it tries `python -m mtkclient`.
- Device detection is heuristic: it scans PnP devices for **MediaTek / Android** hints. If it fails, you can still run actions—just ensure the device is in the correct mode (BootROM/Preloader) and the proper driver is installed.

## 🖥 Drivers
- **Zadig**: If `zadig.exe` is found (PATH or placed next to the app), it will launch. Otherwise, the download page opens.
- **Device Manager**: Shortcut to `devmgmt.msc` for quick driver triage.

## 📝 Logs
- After each action, the live console output is saved to a timestamped `.txt` (e.g., `PhoenixR1_Log_YYYY-mm-dd_HH-MM-SS.txt`).  
- Attach logs in support threads for faster help.

## 🙏 Special Thanks
- **bkerler** — for `mtkclient` and relentless reverse‑engineering
- **Rabbit R1** community — for testing & feedback
- **Breon (“B”)** — vision + pressure = reality

## 🎨 Easter Egg
- Hover on the **One‑Click Restore** button for a second… if you know, you know 🐇🔥

## ⚖️ Legal
This software is provided **as is**, without warranty of any kind. You assume all risk by using it.
