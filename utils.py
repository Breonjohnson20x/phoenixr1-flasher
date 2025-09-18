
import os
import datetime

FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), "firmware")

REQUIRED_IMAGES = {
    "boot": "boot.img",
    "vbmeta": "vbmeta.img",
    # Support either super or system image name
    "super_or_system": ["super.img", "system.img"],
    "vendor": "vendor.img",
}

def list_firmware_images():
    paths = {}
    if not os.path.isdir(FIRMWARE_DIR):
        return paths
    for key, fname in REQUIRED_IMAGES.items():
        if isinstance(fname, list):
            found = None
            for candidate in fname:
                p = os.path.join(FIRMWARE_DIR, candidate)
                if os.path.isfile(p):
                    found = p
                    break
            paths[key] = found
        else:
            p = os.path.join(FIRMWARE_DIR, fname)
            paths[key] = p if os.path.isfile(p) else None
    return paths

def log_filename():
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(os.path.dirname(__file__), f"PhoenixR1_Log_{stamp}.txt")
