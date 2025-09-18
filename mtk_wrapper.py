
import subprocess
import shutil
import sys
import os

def which(cmd):
    return shutil.which(cmd)

def _run(cmd, cwd=None, env=None):
    # Yield lines from process stdout/stderr merged
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    try:
        for line in proc.stdout:
            yield line.rstrip("\n")
    finally:
        proc.wait()

def detect_device():
    """
    Heuristic check for an MTK/Android device on Windows.
    - Try listing USB PnP devices and look for MediaTek/MTK/Android.
    - Fall back to mtk --help presence as a coarse readiness check.
    Returns (connected: bool, detail: str)
    """
    # Check WMIC for device hint (Windows only)
    try:
        out = subprocess.check_output(
            ["wmic", "path", "Win32_PnPEntity", "get", "Name"],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=5
        )
        name = out.lower()
        hits = ["mediatek", "mtk", "android", "preloader", "bootrom", "fastboot"]
        if any(h in name for h in hits):
            return True, "Possible device detected via PnP scan"
    except Exception:
        pass

    # As a soft fallback, if mtk tool exists, we at least can try connecting later
    if which("mtk") or which("mtk.exe") or which("python"):
        return False, "No device found, but tools detected"
    return False, "No device or tools detected"

def open_device_manager():
    # Windows Device Manager
    try:
        subprocess.Popen(["devmgmt.msc"], shell=True)
        return True, "Opened Device Manager"
    except Exception as e:
        return False, str(e)

def open_zadig():
    """
    Try to open zadig.exe if present in PATH or alongside app.
    Otherwise open download page via start command (Windows).
    """
    local = os.path.join(os.path.dirname(__file__), "zadig.exe")
    path_exe = shutil.which("zadig") or shutil.which("zadig.exe") or (local if os.path.isfile(local) else None)
    if path_exe and os.path.isfile(path_exe):
        try:
            subprocess.Popen([path_exe], shell=True)
            return True, f"Opened {path_exe}"
        except Exception as e:
            return False, str(e)
    # Open download page
    try:
        subprocess.Popen(['start', 'https://zadig.akeo.ie/'], shell=True)
        return True, "Opened Zadig download page"
    except Exception as e:
        return False, str(e)

def run_mtk_command(args):
    """
    Run an mtk (mtkclient) CLI command.
    Args is a list, e.g. ["mtk", "w", "boot", "firmware/boot.img"]
    Yields (line:str) for GUI to consume.
    """
    # Prefer 'mtk' command; fallback to 'python -m mtkclient'
    if which("mtk") or which("mtk.exe"):
        cmd = ["mtk"] + args
    else:
        cmd = [sys.executable, "-m", "mtkclient"] + args
    for line in _run(cmd):
        yield line

def flash_partition(partition, image_path):
    # Example: mtk w boot boot.img
    yield from run_mtk_command(["w", partition, image_path])

def reboot_to_bootloader():
    # Example command; adjust to your device/mtkclient version if needed
    yield from run_mtk_command(["reset"])

def wipe_userdata():
    # Danger: wipes data. Confirm at UI level before calling.
    # Often: mtk e userdata  (erase)
    yield from run_mtk_command(["e", "userdata"])

def reset_device():
    # Soft reset via mtk
    yield from run_mtk_command(["reset"])
