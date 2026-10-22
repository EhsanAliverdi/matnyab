"""Build the Windows release: Matnyab.exe (PyInstaller) and Matnyab-Setup-<version>.exe (Inno Setup).

Usage, from the repository root with the build requirements installed:
    python packaging/build.py [--tesseract-dir DIR] [--poppler-dir DIR]

--tesseract-dir   Tesseract install folder (default: C:\\Program Files\\Tesseract-OCR)
--poppler-dir     Poppler folder containing pdftoppm.exe (default: found on PATH)

The installer step runs only when Inno Setup's ISCC.exe is found.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
STAGE = os.path.join(BUILD, "stage")
TESSDATA_LANGS = ["fas", "ara", "eng", "osd"]


def app_version():
    with open(os.path.join(ROOT, "modules", "config.py"), encoding="utf-8") as f:
        return re.search(r'APP_VERSION = "([^"]+)"', f.read()).group(1)


def stage_tesseract(src):
    exe = os.path.join(src, "tesseract.exe")
    if not os.path.isfile(exe):
        sys.exit(f"tesseract.exe not found in {src}")
    dst = os.path.join(STAGE, "tesseract")
    os.makedirs(os.path.join(dst, "tessdata"))
    # The engine and its DLLs only; the training tools aren't needed
    shutil.copy2(exe, dst)
    for name in os.listdir(src):
        if name.lower().endswith(".dll"):
            shutil.copy2(os.path.join(src, name), dst)
    tessdata = os.path.join(src, "tessdata")
    for lang in TESSDATA_LANGS:
        path = os.path.join(tessdata, f"{lang}.traineddata")
        if not os.path.isfile(path):
            sys.exit(f"Missing language data: {path}")
        shutil.copy2(path, os.path.join(dst, "tessdata"))
    for folder in ("configs", "tessconfigs"):
        if os.path.isdir(os.path.join(tessdata, folder)):
            shutil.copytree(os.path.join(tessdata, folder), os.path.join(dst, "tessdata", folder))
    print(f"Staged Tesseract from {src}")


def stage_poppler(src):
    if not src:
        found = shutil.which("pdftoppm")
        if not found:
            sys.exit("Poppler not found. Pass --poppler-dir.")
        src = os.path.dirname(found)
    if not os.path.isfile(os.path.join(src, "pdftoppm.exe")):
        sys.exit(f"pdftoppm.exe not found in {src}")
    dst = os.path.join(STAGE, "poppler")
    os.makedirs(dst)
    for name in os.listdir(src):
        if name.lower().endswith(".dll") or name.lower() in ("pdftoppm.exe", "pdfinfo.exe", "pdftocairo.exe"):
            shutil.copy2(os.path.join(src, name), dst)
    print(f"Staged Poppler from {src}")


def find_iscc():
    candidates = [shutil.which("iscc")]
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")):
        if base:
            candidates.append(os.path.join(base, "Inno Setup 6", "ISCC.exe"))
    return next((c for c in candidates if c and os.path.isfile(c)), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tesseract-dir", default=r"C:\Program Files\Tesseract-OCR")
    parser.add_argument("--poppler-dir", default=None)
    args = parser.parse_args()

    version = app_version()
    print(f"Building Matnyab {version}")
    shutil.rmtree(STAGE, ignore_errors=True)
    stage_tesseract(args.tesseract_dir)
    stage_poppler(args.poppler_dir)

    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", os.path.join(ROOT, "dist"), "--workpath", os.path.join(BUILD, "pyinstaller"),
                    os.path.join(ROOT, "packaging", "matnyab.spec")], check=True)
    print("App built: dist/Matnyab/Matnyab.exe")

    iscc = find_iscc()
    if not iscc:
        print("Inno Setup (ISCC.exe) not found, so no installer was made.")
        return
    subprocess.run([iscc, f"/DAppVersion={version}", os.path.join(ROOT, "packaging", "matnyab.iss")], check=True)
    print(f"Installer built: dist/Matnyab-Setup-{version}.exe")


if __name__ == "__main__":
    main()
