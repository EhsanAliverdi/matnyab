"""User settings (stored with QSettings) and checks for the external OCR tools."""
import os
import shutil
import sys

import pytesseract
from PySide6.QtCore import QSettings

APP_NAME = "Matnyab"
APP_VERSION = "0.1.0"

LANGUAGES = [
    ("Persian", "fas"),
    ("Persian + English", "fas+eng"),
    ("Arabic", "ara"),
    ("English", "eng"),
]

# Installed builds ship Tesseract and Poppler next to Matnyab.exe
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED_TESSERACT = os.path.join(APP_DIR, "tesseract", "tesseract.exe")
BUNDLED_POPPLER = os.path.join(APP_DIR, "poppler")

DEFAULTS = {
    "theme": "dark",
    "language": "fas",
    "dpi": 300,
    "output_folder": "",
    "tesseract_cmd": "",
    "poppler_path": "",
}


class AppConfig:
    def __init__(self):
        self._store = QSettings(APP_NAME, APP_NAME)

    def get(self, key):
        value = self._store.value(key, DEFAULTS[key])
        if isinstance(DEFAULTS[key], int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return DEFAULTS[key]
        return value or DEFAULTS[key]

    def set(self, key, value):
        self._store.setValue(key, value)
        if key == "tesseract_cmd":
            self.apply_tesseract_cmd()

    def tesseract_cmd(self):
        """The Tesseract program to use: the one set in Settings, the bundled one, or PATH."""
        if self.get("tesseract_cmd"):
            return self.get("tesseract_cmd")
        if os.path.isfile(BUNDLED_TESSERACT):
            return BUNDLED_TESSERACT
        return "tesseract"

    def poppler_path(self):
        """Poppler's bin folder: the one set in Settings, the bundled one, or None for PATH."""
        if self.get("poppler_path"):
            return self.get("poppler_path")
        if os.path.isdir(BUNDLED_POPPLER):
            return BUNDLED_POPPLER
        return None

    def apply_tesseract_cmd(self):
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd()


def check_tesseract():
    """Return (ok, message) for the Tesseract executable."""
    try:
        version = str(pytesseract.get_tesseract_version()).split()[0]
        where = " (built in)" if pytesseract.pytesseract.tesseract_cmd == BUNDLED_TESSERACT else ""
        return True, f"Tesseract {version}{where}"
    except Exception:
        return False, "Tesseract not found. Install it or set its path in Settings."


def check_language(lang_code):
    """Return (ok, message) for the Tesseract language data of lang_code (e.g. 'fas+eng')."""
    try:
        installed = set(pytesseract.get_languages(config=""))
    except Exception:
        return False, "Language data can't be checked until Tesseract is found."
    missing = [code for code in lang_code.split("+") if code not in installed]
    if missing:
        return False, f"Missing language data: {', '.join(missing)}.traineddata"
    return True, f"Language data installed ({lang_code})"


def check_poppler(poppler_path):
    """Return (ok, message) for Poppler's pdftoppm, needed to read PDFs."""
    exe = "pdftoppm.exe" if os.name == "nt" else "pdftoppm"
    if poppler_path:
        if os.path.isfile(os.path.join(poppler_path, exe)):
            return True, "Poppler (built in)" if poppler_path == BUNDLED_POPPLER else "Poppler found"
        return False, "pdftoppm was not found in the Poppler folder set in Settings."
    if shutil.which("pdftoppm"):
        return True, "Poppler found on PATH"
    return False, "Poppler not found. PDF files can't be read until it's installed."
