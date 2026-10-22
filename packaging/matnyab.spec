# PyInstaller spec for Matnyab. Run through packaging/build.py, or:
#   pyinstaller --noconfirm --clean packaging/matnyab.spec
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    datas=[
        (os.path.join(ROOT, "themes"), "themes"),
        (os.path.join(ROOT, "icon.ico"), "."),
    ],
    # ui_functions does "from main import *", so main.py is also needed as a module
    hiddenimports=["main"],
    excludes=["PySide2", "PyQt5", "PyQt6", "tkinter", "matplotlib", "IPython"],
    noarchive=False,
)
# Large libraries the app never uses: OpenCV's video I/O, Qt's software OpenGL,
# Qt Quick and Qt's translations. Qt6Qml itself must stay: pyside6.abi3.dll links to it.
UNUSED = ("opencv_videoio_ffmpeg", "opengl32sw", "Qt6Quick", "QtQuick", "Qt6QmlModels",
          "Qt6QmlWorkerScript", "Qt6VirtualKeyboard", "Qt6Pdf", os.path.join("PySide6", "translations"))


def keep(entry):
    return not any(part.lower() in entry[0].lower() for part in UNUSED)


a.binaries = [b for b in a.binaries if keep(b)]
a.datas = [d for d in a.datas if keep(d)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Matnyab",
    icon=os.path.join(ROOT, "icon.ico"),
    console=False,
    upx=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="Matnyab",
    upx=False,
)
