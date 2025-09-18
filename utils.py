# utils.py
import os
import sys
import json
from pathlib import Path
from datetime import datetime

CONFIG_NAME = "phoenix_config.json"

PHOENIX_FILENAMES = {
    "boot": ["boot.img", "boot_a.img", "boot.bin", "boot_a.bin"],
    "vbmeta": ["vbmeta.img", "vbmeta_a.img", "vbmeta.bin", "vbmeta_a.bin"],
    "super_or_system": ["super.img", "super.bin", "system.img", "system.bin"],
    "vendor": [
        "vendor.img", "vendor.bin",
        "vendor_boot.img", "vendor_boot.bin"  # last-resort only
    ],
}

def _app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

# --------------------
# Config (persisted)
# --------------------
def _cfg_path() -> Path:
    return _app_dir() / CONFIG_NAME

def load_config() -> dict:
    p = _cfg_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_config(cfg: dict) -> None:
    try:
        _cfg_path().write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception:
        pass

def get_mtk_path() -> str | None:
    return load_config().get("mtk_path")

def set_mtk_path(path: str | None) -> None:
    cfg = load_config()
    if path:
        cfg["mtk_path"] = path
    else:
        cfg.pop("mtk_path", None)
    save_config(cfg)

def get_fw_dir() -> str | None:
    return load_config().get("fw_dir")

def set_fw_dir(path: str | None) -> None:
    cfg = load_config()
    if path:
        cfg["fw_dir"] = path
    else:
        cfg.pop("fw_dir", None)
    save_config(cfg)

# --------------------
# Firmware discovery
# --------------------
def _find_first(candidates, base: Path):
    base = Path(base)
    files = {p.name.lower(): p for p in base.rglob("*") if p.is_file()}
    for name in candidates:
        p = files.get(name.lower())
        if p:
            return str(p)
    return None

def list_firmware_images(preferred_dir: str | None = None) -> dict:
    """
    Search order:
      1) preferred_dir (user chosen)
      2) <app>/firmware
      3) <app>
    """
    paths = {"boot": None, "vbmeta": None, "super_or_system": None, "vendor": None}
    roots: list[Path] = []

    if preferred_dir and Path(preferred_dir).exists():
        roots.append(Path(preferred_dir))

    appd = _app_dir()
    fw = appd / "firmware"
    if fw.exists():
        roots.append(fw)
    roots.append(appd)

    seen, ordered = set(), []
    for r in roots:
        rr = r.resolve()
        if rr not in seen:
            ordered.append(rr)
        seen.add(rr)

    for root in ordered:
        for key, names in PHOENIX_FILENAMES.items():
            if paths[key]:
                continue
            hit = _find_first(names, root)
            if hit:
                # accept vendor_boot only if nothing else ever appears
                if key == "vendor" and Path(hit).name.lower().startswith("vendor_boot"):
                    paths[key] = paths[key] or hit
                else:
                    paths[key] = hit
    return paths

# --------------------
# Logs
# --------------------
def log_filename() -> str:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return str(_app_dir() / f"PhoenixR1_Log_{ts}.txt")
