# Matnyab (متن‌یاب)

A desktop app that turns scanned Persian (Farsi) documents into editable text.

Point it at an image, a PDF or a whole folder of scans, and Matnyab cleans up each page,
runs it through Tesseract's Farsi model and saves the result as plain text and/or a
Microsoft Word document.

## Download

Get the Windows installer from the
[latest release](https://github.com/EhsanAliverdi/matnyab/releases/latest)
(`Matnyab-Setup-<version>.exe`). It includes everything the app needs, including Tesseract OCR with
Persian, Arabic and English data and Poppler for PDFs, so there's nothing else to install.

The installer isn't code-signed yet, so Windows SmartScreen may warn about it:
choose **More info → Run anyway**.

## Features

- **Image OCR** – recognise a single `.png`, `.jpg`, `.jpeg` or `.tiff` image
- **PDF OCR** – split a scanned PDF into pages and recognise every page
- **Batch OCR** – process every image and PDF in a folder
- **Output options** – `.txt` and/or `.docx`, as one merged file or one file per page
- **Languages** – Persian, Persian + English, Arabic or English
- Progress bar and status while converting, with a shortcut to the output folder
- Built-in system check for Tesseract, its language data and Poppler
- Settings for theme, default output folder, language, scan resolution and tool paths
- Image preprocessing with OpenCV (resize to OCR-friendly resolution, noise removal)
- Dark and light themes

## Requirements

- Windows (tested), Python 3.9+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) with the Persian language data
  (`fas.traineddata`, from [tessdata](https://github.com/tesseract-ocr/tessdata)) in Tesseract's `tessdata` folder
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) on your `PATH` (needed to read PDFs)

If Tesseract or Poppler aren't on your `PATH`, set their locations on the Settings page.
The Home page shows whether everything was found.

## Running from source

```console
pip install -r requirements.txt
python main.py
```

## Rebuilding the UI and resources

After editing `main.ui`, `resources.qrc` or the images:

```console
pyside6-uic main.ui -o modules/ui_main.py
pyside6-rcc resources.qrc -o modules/resources_rc.py
```

Then change `import resources_rc` at the top of `modules/ui_main.py` to `from .resources_rc import *`.

## Building the installer

The installer is built automatically by GitHub Actions
([.github/workflows/release.yml](.github/workflows/release.yml)) when a version tag is pushed:

1. Set `APP_VERSION` in `modules/config.py`, e.g. `0.2.0`
2. Commit, then tag and push: `git tag v0.2.0` and `git push origin v0.2.0`

The workflow builds the app, tests the packaged build on a sample PDF, and publishes a release
with the installer attached.

To build locally you need Python 3.9, Tesseract (with `fas`, `ara`, `eng` and `osd` data),
Poppler and, for the installer step, [Inno Setup 6](https://jrsoftware.org/isinfo.php):

```console
python -m venv .venv
.venv\Scripts\pip install -r requirements-build.txt
.venv\Scripts\python packaging/build.py --poppler-dir "C:\path	o\poppler\Libraryin"
```

The app is written to `dist/Matnyab/` and the installer to `dist/Matnyab-Setup-<version>.exe`.

## Project layout

| Path | What it is |
|---|---|
| `main.py` | App entry point: main window, navigation, themes, running OCR jobs |
| `main.ui` | Qt Designer layout of the window shell (compiled to `modules/ui_main.py`) |
| `modules/pages.py` | Home, PDF, Image, Batch and Settings pages |
| `modules/config.py` | Saved settings and checks for Tesseract / Poppler |
| `modules/OCR/src/ocr.py` | OCR pipeline: PDF → images → preprocessing → Tesseract → txt/docx |
| `modules/OCR/src/preprocess.py` | OpenCV image clean-up |
| `modules/worker.py` | Background worker so the UI stays responsive |
| `themes/` | Qt stylesheets |
| `packaging/` | PyInstaller spec, Inno Setup script and build script for the Windows installer |
| `tools/make_icons.py` | Draws the logo, `icon.ico` and every UI icon in one shared style |
| `examples/` | Sample output |

## Credits

- User interface based on [PyDracula](https://github.com/Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6)
  by Wanderson M. Pimenta (MIT, see `LICENSE`).
- OCR pipeline based on FarsiOCR by Sajedeh Tafazzoli
  (MIT, see `modules/OCR/LICENSE`).
- Text recognition by [Tesseract OCR](https://github.com/tesseract-ocr/tesseract).
