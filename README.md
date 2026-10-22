# Matnyab (متن‌یاب)

A desktop app that turns scanned Persian (Farsi) documents into editable text.

Point it at an image, a PDF or a whole folder of scans, and Matnyab cleans up each page,
runs it through Tesseract's Farsi model and saves the result as plain text and/or a
Microsoft Word document.

## Features

- **Image OCR** – recognise a single `.png`, `.jpg`, `.jpeg` or `.tiff` image
- **PDF OCR** – split a scanned PDF into pages and recognise every page
- **Batch OCR** – process every image and PDF in a folder
- **Output options** – `.txt` and/or `.docx`, as one merged file or one file per page
- Image preprocessing with OpenCV (resize to OCR-friendly resolution, noise removal)
- Dark and light themes

## Requirements

- Windows (tested), Python 3.9+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) with the Persian language data
  (`fas.traineddata`, from [tessdata](https://github.com/tesseract-ocr/tessdata)) in Tesseract's `tessdata` folder
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) on your `PATH` (needed to read PDFs)

## Getting started

```console
pip install -r requirements.txt
python main.py
```

## Building an executable

```console
pip install cx_Freeze
python setup.py build
```

## Project layout

| Path | What it is |
|---|---|
| `main.py` | App entry point and main window logic |
| `main.ui` | Qt Designer layout (compiled to `modules/ui_main.py`) |
| `modules/OCR/src/ocr.py` | OCR pipeline: PDF → images → preprocessing → Tesseract → txt/docx |
| `modules/OCR/src/preprocess.py` | OpenCV image clean-up |
| `modules/worker.py` | Background worker so the UI stays responsive |
| `themes/` | Qt stylesheets |
| `examples/` | Sample output |

## Credits

- User interface based on [PyDracula](https://github.com/Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6)
  by Wanderson M. Pimenta (MIT, see `LICENSE`).
- OCR pipeline based on FarsiOCR by Sajedeh Tafazzoli
  (MIT, see `modules/OCR/LICENSE`).
- Text recognition by [Tesseract OCR](https://github.com/tesseract-ocr/tesseract).
