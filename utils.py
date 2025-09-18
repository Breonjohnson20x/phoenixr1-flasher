# utils.py
import os
import sys
from pathlib import Path
from datetime import datetime

PHOENIX_FILENAMES = {
    "boot": ["boot.img", "boot_a.img", "boot.bin", "boot_a.bin"],
    "vbmeta": ["vbmeta.img", "vbmeta_a.img", "vbmeta.bin", "vbmeta_a.bin"],
    # super OR system — accept either; super preferred if both exist
    "super_or_system": ["super.img", "super.bin", "system.img", "system.bin"],
    "vendor": [
        "vendor.img", "vendor.bin",
        # Some dumps mislabel vendor as vendor_boot; try last
        "vendor_boot.img", "vendor_boot.bin"
    ],
}

def _app_dir() -> Path:
    """Directory of the running app (works for PyInstaller .exe and plain Python)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

def _find_first(candidates, base: Path):
    base = Path(base)
    lower_map = {p.name.lower(): p for p in base.rglob("*") if p.is_file()}
    for name in candidates:
        p = lower_map.get(name.lower())
        if p:
            return str(p)
    return None

def list_firmware_images(preferred_dir: str | None = None) -> dict:
    """
    Returns a dict with keys: boot, vbmeta, super_or_system, vendor
    Searching order:
      1) preferred_dir (user chosen)
      2) <app>/firmware
      3) <app> (same folder as the EXE)
    """
    paths = {"boot": None, "vbmeta": None, "super_or_system": None, "vendor": None}
    search_roots: list[Path] = []

    if preferred_dir and Path(preferred_dir).exists():
        search_roots.append(Path(preferred_dir))

    appd = _app_dir()
    fw = appd / "firmware"
    if fw.exists():
        search_roots.append(fw)

    search_roots.append(appd)

    # Remove dup roots, keep order
    seen = set()
    ordered_roots = []
    for r in search_roots:
        rp = r.resolve()
        if rp not in seen:
            ordered_roots.append(rp)
            seen.add(rp)

    # Fill from first hit in root order
    for root in ordered_roots:
        for key, names in PHOENIX_FILENAMES.items():
            if paths[key]:
                continue
            found = _find_first(names, root)
            if found:
                # Heuristic: mark vendor_boot only if nothing else appears later
                if key == "vendor" and Path(found).name.lower().startswith("vendor_boot"):
                    paths[key] = paths[key] or found
                else:
                    paths[key] = found

    return paths

def log_filename() -> str:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return str(_app_dir() / f"PhoenixR1_Log_{ts}.txt")
