"""Draw the Matnyab logo and app icon.

Run from the repository root:  python tools/make_icons.py
Writes images/images/logo_*.png and icon.ico, then recompile resources with
pyside6-rcc resources.qrc -o modules/resources_rc.py
"""
import io
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")

from PIL import Image
from PySide6.QtCore import QBuffer, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QFont, QGuiApplication, QImage, QLinearGradient,
                           QPainter, QPainterPath, QPen)

PURPLE = QColor("#bd93f9")
PINK = QColor("#ff79c6")
DARK = QColor("#282a36")


def draw_logo(size: int) -> QImage:
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    s = size / 100.0

    # Rounded square with the Dracula purple -> pink gradient
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, PURPLE)
    grad.setColorAt(1, PINK)
    p.setPen(Qt.NoPen)
    p.setBrush(grad)
    p.drawRoundedRect(QRectF(2 * s, 2 * s, 96 * s, 96 * s), 22 * s, 22 * s)

    # Persian word "matn" (text)
    # Drawn as an outlined path so the strokes stay bold at small sizes
    font = QFont("Tahoma", 1, QFont.Bold)
    font.setPixelSize(int(50 * s))
    text = QPainterPath()
    text.addText(0, 0, font, "متن")
    box = text.boundingRect()
    text.translate(44 * s - box.center().x(), 36 * s - box.center().y())
    p.setBrush(QColor("#ffffff"))
    p.setPen(QPen(QColor("#ffffff"), 2.5 * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPath(text)

    # Magnifying glass: the "find" in Matnyab
    lens = QPointF(70 * s, 68 * s)
    p.setBrush(QColor(255, 255, 255, 60))
    p.setPen(QPen(DARK, 7 * s))
    p.drawEllipse(lens, 15 * s, 15 * s)
    pen = QPen(DARK, 9 * s)
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)
    p.drawLine(QPointF(81 * s, 79 * s), QPointF(91 * s, 89 * s))
    p.end()
    return img


def to_pil(img: QImage) -> Image.Image:
    buf = QBuffer()
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return Image.open(io.BytesIO(bytes(buf.data())))


def main():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "images", "images")
    for size in (40, 160):
        draw_logo(size).save(os.path.join(out, f"logo_{size}.png"))
    big = to_pil(draw_logo(256))
    big.save(os.path.join(root, "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Logo and icon written.")


if __name__ == "__main__":
    main()
