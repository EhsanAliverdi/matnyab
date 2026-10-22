"""Draw Matnyab's logo, app icon and UI icons so they all share one style.

Run from the repository root:  python tools/make_icons.py
Then recompile resources:      pyside6-rcc resources.qrc -o modules/resources_rc.py

Every glyph is drawn on a 24x24 grid with rounded strokes. The same glyphs are
used for the side menu (white, 20 px) and the home page tiles (white on the
brand gradient, like the logo).
"""
import io
import math
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")

from PIL import Image
from PySide6.QtCore import QBuffer, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QFont, QGuiApplication, QImage, QLinearGradient,
                           QPainter, QPainterPath, QPen)

# Brand colours (Dracula purple -> pink)
BRAND_START = QColor("#bd93f9")
BRAND_END = QColor("#ff79c6")
MENU_ICON = QColor(230, 230, 230)
LIGHT_THEME_ICON = QColor("#795da9")  # light theme accent, for icons on light backgrounds
WHITE = QColor("#ffffff")


# ---------------------------------------------------------------------------
# Glyphs, drawn on a 24x24 grid
# ---------------------------------------------------------------------------

def glyph_home(p):
    p.drawPolyline([QPointF(3, 11), QPointF(12, 3.5), QPointF(21, 11)])
    path = QPainterPath()
    path.moveTo(5.5, 9.5)
    path.lineTo(5.5, 20.5)
    path.lineTo(18.5, 20.5)
    path.lineTo(18.5, 9.5)
    p.drawPath(path)
    p.drawPolyline([QPointF(10, 20.5), QPointF(10, 14.5), QPointF(14, 14.5), QPointF(14, 20.5)])


def _page(p, x, y, w, h, fold=4.5, lines=3):
    path = QPainterPath()
    path.moveTo(x, y)
    path.lineTo(x + w - fold, y)
    path.lineTo(x + w, y + fold)
    path.lineTo(x + w, y + h)
    path.lineTo(x, y + h)
    path.closeSubpath()
    p.drawPath(path)
    p.drawPolyline([QPointF(x + w - fold, y), QPointF(x + w - fold, y + fold), QPointF(x + w, y + fold)])
    for i in range(lines):
        ly = y + fold + 4 + i * 3.2
        lw = w - 5 if i < lines - 1 else (w - 5) * 0.6
        p.drawLine(QPointF(x + 2.5, ly), QPointF(x + 2.5 + lw, ly))


def glyph_pdf(p):
    _page(p, 5, 2.5, 14, 19)


def glyph_image(p):
    p.drawRoundedRect(QRectF(2.5, 4.5, 19, 15), 2.5, 2.5)
    p.drawEllipse(QPointF(8.5, 9.5), 1.8, 1.8)
    p.drawPolyline([QPointF(3, 18), QPointF(9, 12.5), QPointF(13, 16),
                    QPointF(16, 13.5), QPointF(21, 18)])


def glyph_batch(p):
    # Two pages behind a front page
    p.drawPolyline([QPointF(9, 2.5), QPointF(20.5, 2.5), QPointF(20.5, 16)])
    p.drawPolyline([QPointF(6, 5.5), QPointF(17.5, 5.5), QPointF(17.5, 19)])
    _page(p, 3, 8.5, 11.5, 13, fold=3.5, lines=2)


def glyph_settings(p):
    teeth, r_out, r_in = 8, 10, 7.3
    path = QPainterPath()
    for k in range(teeth):
        a = 360 / teeth * k
        for da, r in ((-15, r_in), (-8, r_out), (8, r_out), (15, r_in)):
            t = math.radians(a + da)
            pt = QPointF(12 + r * math.cos(t), 12 + r * math.sin(t))
            if k == 0 and da == -15:
                path.moveTo(pt)
            else:
                path.lineTo(pt)
    path.closeSubpath()
    p.drawPath(path)
    p.drawEllipse(QPointF(12, 12), 3, 3)


def glyph_menu(p):
    for y in (6, 12, 18):
        p.drawLine(QPointF(4, y), QPointF(20, y))


def glyph_search(p):
    p.drawEllipse(QPointF(10.5, 10.5), 6, 6)
    p.drawLine(QPointF(15, 15), QPointF(20.5, 20.5))


def glyph_close(p):
    p.drawLine(QPointF(6, 6), QPointF(18, 18))
    p.drawLine(QPointF(18, 6), QPointF(6, 18))


def glyph_minimize(p):
    p.drawLine(QPointF(6, 12), QPointF(18, 12))


def glyph_maximize(p):
    p.drawRoundedRect(QRectF(6, 6, 12, 12), 1.5, 1.5)


def glyph_restore(p):
    p.drawRoundedRect(QRectF(5, 9, 10, 10), 1.5, 1.5)
    p.drawPolyline([QPointF(9, 6), QPointF(18, 6), QPointF(18, 15)])


def glyph_check(p):
    p.drawPolyline([QPointF(5, 12.5), QPointF(10, 17.5), QPointF(19, 7)])


def glyph_chevron_down(p):
    p.drawPolyline([QPointF(6, 9), QPointF(12, 15), QPointF(18, 9)])


# Small UI glyphs: (name, function, pixel size, stroke width on the 24 grid, colour)
UI_ICONS = [
    ("win_close", glyph_close, 20, 1.8, MENU_ICON),
    ("win_minimize", glyph_minimize, 20, 1.8, MENU_ICON),
    ("win_maximize", glyph_maximize, 20, 1.8, MENU_ICON),
    ("win_restore", glyph_restore, 20, 1.8, MENU_ICON),
    ("ui_check", glyph_check, 16, 3, WHITE),
    ("ui_check_dark", glyph_check, 16, 3, QColor("#282a36")),
    ("ui_chevron_down", glyph_chevron_down, 16, 2.4, MENU_ICON),
    ("ui_chevron_down_light", glyph_chevron_down, 16, 2.4, LIGHT_THEME_ICON),
]

GLYPHS = {
    "home": glyph_home,
    "pdf": glyph_pdf,
    "image": glyph_image,
    "batch": glyph_batch,
    "settings": glyph_settings,
    "menu": glyph_menu,
}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _canvas(size):
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    return img, p


def _pen(color, width):
    return QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)


def _tile(p, size):
    """The brand gradient rounded square shared by the logo and the home tiles."""
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, BRAND_START)
    grad.setColorAt(1, BRAND_END)
    p.setPen(Qt.NoPen)
    p.setBrush(grad)
    m = size * 0.02
    p.drawRoundedRect(QRectF(m, m, size - 2 * m, size - 2 * m), size * 0.22, size * 0.22)


def draw_line_icon(glyph, size=20, stroke=1.7, color=MENU_ICON):
    img, p = _canvas(size)
    p.scale(size / 24, size / 24)
    p.setPen(_pen(color, stroke))
    p.setBrush(Qt.NoBrush)
    glyph(p)
    p.end()
    return img


def draw_tile(name, size=72):
    img, p = _canvas(size)
    _tile(p, size)
    # Glyph fills the middle 55% of the tile
    inner = size * 0.55
    p.translate((size - inner) / 2, (size - inner) / 2)
    p.scale(inner / 24, inner / 24)
    p.setPen(_pen(WHITE, 2))
    p.setBrush(Qt.NoBrush)
    GLYPHS[name](p)
    p.end()
    return img


def draw_logo(size):
    img, p = _canvas(size)
    _tile(p, size)
    s = size / 100.0

    # Persian word "matn" (text), drawn as a path so it stays bold when small
    font = QFont("Tahoma", 1, QFont.Bold)
    font.setPixelSize(int(54 * s))
    text = QPainterPath()
    text.addText(0, 0, font, "متن")
    box = text.boundingRect()
    text.translate(42 * s - box.center().x(), 37 * s - box.center().y())
    p.setBrush(WHITE)
    p.setPen(_pen(WHITE, 2.2 * s))
    p.drawPath(text)

    # Magnifying glass: the "find" in Matnyab, same glyph as the UI icons
    p.translate(56 * s, 54 * s)
    p.scale(36 * s / 24, 36 * s / 24)
    p.setBrush(QColor(255, 255, 255, 50))
    p.setPen(_pen(WHITE, 3))
    glyph_search(p)
    p.end()
    return img


def to_pil(img):
    buf = QBuffer()
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return Image.open(io.BytesIO(bytes(buf.data())))


def main():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images = os.path.join(root, "images", "images")
    icons = os.path.join(root, "images", "icons")

    for size in (40, 160):
        draw_logo(size).save(os.path.join(images, f"logo_{size}.png"))
    for name, glyph in GLYPHS.items():
        draw_line_icon(glyph).save(os.path.join(icons, f"nav_{name}.png"))
    for name, glyph, size, stroke, color in UI_ICONS:
        draw_line_icon(glyph, size, stroke, color).save(os.path.join(icons, f"{name}.png"))
    for name in ("pdf", "image", "batch"):
        draw_tile(name).save(os.path.join(icons, f"tile_{name}.png"))

    big = to_pil(draw_logo(256))
    big.save(os.path.join(root, "icon.ico"),
             sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Logo, app icon and UI icons written.")


if __name__ == "__main__":
    main()
