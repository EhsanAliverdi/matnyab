# Third-party software in the Matnyab installer

The Windows installer bundles these programs so Matnyab works without any
other installation. Each keeps its own license.

| Component | Used for | License | Source code |
|---|---|---|---|
| Tesseract OCR | Text recognition | Apache License 2.0 | https://github.com/tesseract-ocr/tesseract |
| Tesseract language data (fas, ara, eng, osd) | Recognition models | Apache License 2.0 | https://github.com/tesseract-ocr/tessdata_fast |
| Poppler | Reading PDF pages | GNU GPL v2 or later | https://poppler.freedesktop.org/ |
| Qt for Python (PySide6) | User interface | GNU LGPL v3 | https://code.qt.io/cgit/pyside/pyside-setup.git/ |
| Python | Runtime | PSF License | https://www.python.org/ |
| OpenCV, NumPy, Pillow, pdf2image, pytesseract, python-docx, natsort | Image processing and output | BSD / MIT / Apache 2.0 / HPND | See each project on PyPI |
| PyDracula | Window design | MIT | https://github.com/Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6 |
| FarsiOCR | Original OCR pipeline | MIT | — |

The Windows builds of Tesseract and Poppler come from
https://github.com/UB-Mannheim/tesseract and
https://github.com/oschwartz10612/poppler-windows.
