"""Content pages shown in the main window's stacked widget.

The window shell (title bar, side menu, theme) comes from main.ui; the pages are
built here in code so each one only contains working controls.
"""
import os

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QFrame, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton,
                               QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

from .config import APP_NAME, APP_VERSION, LANGUAGES, check_language, check_poppler, check_tesseract

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']
DPI_CHOICES = [150, 200, 300, 400, 600]

PALETTES = {
    "dark": {"card": "rgb(33, 37, 43)", "border": "rgb(52, 59, 72)", "text": "rgb(221, 221, 221)",
             "muted": "rgb(130, 140, 160)", "accent": "#bd93f9", "accent_text": "#282a36",
             "accent_hover": "#cba6fa", "ok": "#50fa7b", "error": "#ff5555", "hover": "rgb(40, 44, 52)",
             "input": "rgb(27, 29, 35)"},
    "light": {"card": "#ffffff", "border": "#d6d9e0", "text": "#333333",
              "muted": "#795da9", "accent": "#795da9", "accent_text": "#ffffff",
              "accent_hover": "#8c70bd", "ok": "#2e9d4c", "error": "#d63c3c", "hover": "#f0f1f6",
              "input": "#eef0f5"},
}


def page_stylesheet(theme):
    c = PALETTES[theme]
    return f"""
    QScrollArea {{ background: transparent; }} #pageBody {{ background: transparent; }}
    #pageTitle {{ font: 600 18pt "Segoe UI"; color: {c['text']}; }}
    #pageSubtitle {{ font: 10pt "Segoe UI"; color: {c['muted']}; }}
    #card {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 10px; }}
    #card QLabel {{ background: transparent; border: none; }}
    #cardTitle {{ font: 600 11pt "Segoe UI"; color: {c['text']}; }}
    #fieldLabel {{ color: {c['muted']}; }}
    #hint {{ color: {c['muted']}; font-size: 9pt; }}
    #statusOk {{ color: {c['ok']}; }}
    #statusError {{ color: {c['error']}; }}
    QLineEdit, QComboBox {{ min-height: 30px; background-color: {c['input']}; color: {c['text']};
        border: 2px solid {c['input']}; border-radius: 5px; padding-left: 10px; }}
    QLineEdit:hover, QComboBox:hover {{ border: 2px solid {c['border']}; }}
    QLineEdit:focus, QComboBox:focus {{ border: 2px solid {c['accent']}; }}
    QLineEdit:disabled, QComboBox:disabled {{ color: {c['muted']}; }}
    QComboBox QAbstractItemView {{ background-color: {c['card']}; color: {c['text']}; padding: 6px;
        selection-background-color: {c['accent']}; selection-color: {c['accent_text']}; }}
    QComboBox::drop-down {{ border: none; border-left: 1px solid {c['border']}; width: 26px; }}
    QPushButton#browseButton {{ min-height: 30px; min-width: 110px; padding: 0 12px; color: {c['text']};
        background-color: {c['input']}; border: 1px solid {c['border']}; border-radius: 5px; }}
    QPushButton#browseButton:hover {{ border: 1px solid {c['accent']}; }}
    QPushButton#browseButton:disabled {{ color: {c['muted']}; }}
    QPushButton#primaryButton {{ background-color: {c['accent']}; color: {c['accent_text']};
        font: 600 11pt "Segoe UI"; border-radius: 6px; min-height: 40px; border: none; }}
    QPushButton#primaryButton:hover {{ background-color: {c['accent_hover']}; }}
    QPushButton#primaryButton:disabled {{ background-color: {c['border']}; color: {c['muted']}; }}
    QPushButton#actionCard {{ background-color: {c['card']}; border: 1px solid {c['border']};
        border-radius: 12px; text-align: left; padding: 16px; }}
    QPushButton#actionCard:hover {{ background-color: {c['hover']}; border: 1px solid {c['accent']}; }}
    QProgressBar {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 6px;
        min-height: 14px; max-height: 14px; text-align: center; color: transparent; }}
    QProgressBar::chunk {{ background-color: {c['accent']}; border-radius: 5px; }}
    """


# ---------------------------------------------------------------------------
# Small building blocks
# ---------------------------------------------------------------------------

def card(title=None):
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 16, 20, 18)
    layout.setSpacing(10)
    if title:
        label = QLabel(title)
        label.setObjectName("cardTitle")
        layout.addWidget(label)
    return frame, layout


def header(title, subtitle):
    box = QVBoxLayout()
    box.setSpacing(4)
    t = QLabel(title)
    t.setObjectName("pageTitle")
    s = QLabel(subtitle)
    s.setObjectName("pageSubtitle")
    s.setWordWrap(True)
    box.addWidget(t)
    box.addWidget(s)
    return box


def status_label(ok, text):
    label = QLabel(("✓  " if ok else "✗  ") + text)
    label.setObjectName("statusOk" if ok else "statusError")
    label.setWordWrap(True)
    return label


class PathField(QWidget):
    """A line edit with a Browse button, for a file or a folder."""
    changed = Signal(str)

    def __init__(self, placeholder, mode="folder", file_filter="", button_text="Browse..."):
        super().__init__()
        self.mode = mode
        self.file_filter = file_filter
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.textChanged.connect(self.changed)
        self.button = QPushButton(button_text)
        self.button.setObjectName("browseButton")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.clicked.connect(self.browse)
        layout.addWidget(self.edit, 1)
        layout.addWidget(self.button)

    def browse(self):
        start = self.text() or os.path.expanduser("~")
        if self.mode == "file":
            path, _ = QFileDialog.getOpenFileName(self, "Choose a file", start, self.file_filter)
        elif self.mode == "exe":
            path, _ = QFileDialog.getOpenFileName(self, "Choose the program", start, "Programs (*.exe);;All files (*)")
        else:
            path = QFileDialog.getExistingDirectory(self, "Choose a folder", start)
        if path:
            self.setText(os.path.normpath(path))

    def text(self):
        return self.edit.text().strip()

    def setText(self, value):
        self.edit.setText(value)


class ScrollPage(QScrollArea):
    """Scrollable page with a centred, width-limited content column."""

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        body.setObjectName("pageBody")
        outer = QHBoxLayout(body)
        outer.setContentsMargins(30, 26, 30, 26)
        column = QWidget()
        column.setMaximumWidth(860)
        self.column = QVBoxLayout(column)
        self.column.setContentsMargins(0, 0, 0, 0)
        self.column.setSpacing(16)
        outer.addWidget(column)
        self.setWidget(body)


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

class HomePage(ScrollPage):
    navigate = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        col = self.column

        hero = QHBoxLayout()
        hero.setSpacing(20)
        logo = QLabel()
        logo.setPixmap(QPixmap(":/images/images/images/logo_160.png").scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        hero.addWidget(logo)
        hero.addLayout(header(APP_NAME, "Turn scanned Persian (Farsi) documents into editable text. "
                                        "Choose what you want to convert to get started."), 1)
        col.addLayout(hero)

        actions = QGridLayout()
        actions.setSpacing(14)
        items = [
            ("pdf", ":/icons/images/icons/tile_pdf.png", "PDF to Text", "Convert every page of a scanned PDF."),
            ("image", ":/icons/images/icons/tile_image.png", "Image to Text", "Convert a single scanned image or photo."),
            ("batch", ":/icons/images/icons/tile_batch.png", "Batch Folder", "Convert all images and PDFs in a folder."),
        ]
        for i, (key, icon, title, text) in enumerate(items):
            actions.addWidget(self._action_card(key, icon, title, text), 0, i)
        col.addLayout(actions)

        self.status_card, self.status_layout = card("System check")
        col.addWidget(self.status_card)
        self.refresh_status()
        col.addStretch(1)

    def _action_card(self, key, icon, title, text):
        button = QPushButton()
        button.setObjectName("actionCard")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(190)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.clicked.connect(lambda: self.navigate.emit(key))
        layout = QVBoxLayout(button)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(6)
        pic = QLabel()
        pic.setPixmap(QPixmap(icon))
        pic.setAttribute(Qt.WA_TransparentForMouseEvents)
        t = QLabel(title)
        t.setObjectName("cardTitle")
        t.setAttribute(Qt.WA_TransparentForMouseEvents)
        d = QLabel(text)
        d.setObjectName("hint")
        d.setWordWrap(True)
        d.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(pic)
        layout.addStretch(1)
        layout.addWidget(t)
        layout.addWidget(d)
        return button

    def refresh_status(self):
        while self.status_layout.count() > 1:
            item = self.status_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        tess_ok, tess_msg = check_tesseract()
        checks = [(tess_ok, tess_msg)]
        if tess_ok:
            checks.append(check_language(self.config.get("language")))
        checks.append(check_poppler(self.config.poppler_path()))
        for ok, msg in checks:
            self.status_layout.addWidget(status_label(ok, msg))


# ---------------------------------------------------------------------------
# OCR pages (PDF, image, batch)
# ---------------------------------------------------------------------------

OCR_MODES = {
    "pdf": {
        "title": "PDF to Text",
        "subtitle": "Recognise the text on every page of a scanned PDF.",
        "input_label": "PDF file",
        "missing_input": "Choose a PDF file first.",
        "placeholder": "Choose a scanned PDF file...",
        "input_mode": "file",
        "filter": "PDF files (*.pdf)",
        "layout": True,
    },
    "image": {
        "title": "Image to Text",
        "subtitle": "Recognise the text in a single scanned page or photo.",
        "input_label": "Image file",
        "missing_input": "Choose an image file first.",
        "placeholder": "Choose an image (PNG, JPG or TIFF)...",
        "input_mode": "file",
        "filter": "Images (" + " ".join("*" + e for e in IMAGE_EXTENSIONS) + ")",
        "layout": False,
    },
    "batch": {
        "title": "Batch Folder",
        "subtitle": "Recognise every image and PDF in a folder. Each file gets its own output.",
        "input_label": "Input folder",
        "missing_input": "Choose an input folder first.",
        "placeholder": "Choose a folder of images and PDFs...",
        "input_mode": "folder",
        "filter": "",
        "layout": True,
    },
}


class OcrPage(ScrollPage):
    start_requested = Signal(str)

    def __init__(self, mode, config):
        super().__init__()
        self.mode = mode
        self.config = config
        spec = OCR_MODES[mode]
        col = self.column
        col.addLayout(header(spec["title"], spec["subtitle"]))

        # Files
        files, fl = card("Files")
        fl.addWidget(self._field_label(spec["input_label"]))
        self.input = PathField(spec["placeholder"], spec["input_mode"], spec["filter"])
        self.input.changed.connect(self._suggest_output)
        fl.addWidget(self.input)
        fl.addWidget(self._field_label("Save results to"))
        self.output = PathField("Choose the folder for the text files...")
        self.output.setText(config.get("output_folder"))
        fl.addWidget(self.output)
        col.addWidget(files)

        # Options
        options, ol = card("Options")
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(8)
        grid.addWidget(self._field_label("Output format"), 0, 0)
        self.txt_chk = QCheckBox("Plain text (.txt)")
        self.txt_chk.setChecked(True)
        self.docx_chk = QCheckBox("Microsoft Word (.docx)")
        self.docx_chk.setChecked(True)
        grid.addWidget(self.txt_chk, 1, 0)
        grid.addWidget(self.docx_chk, 2, 0)

        self.single_chk = QCheckBox("One combined file")
        self.single_chk.setChecked(True)
        self.per_page_chk = QCheckBox("One file per page")
        if spec["layout"]:
            grid.addWidget(self._field_label("Output layout"), 0, 1)
            grid.addWidget(self.single_chk, 1, 1)
            grid.addWidget(self.per_page_chk, 2, 1)

        grid.addWidget(self._field_label("Document language"), 0, 2)
        self.language = QComboBox()
        for name, code in LANGUAGES:
            self.language.addItem(name, code)
        grid.addWidget(self.language, 1, 2)
        grid.setColumnStretch(3, 1)
        ol.addLayout(grid)
        col.addWidget(options)

        # Run
        run, rl = card()
        self.convert_btn = QPushButton("Convert to Text")
        self.convert_btn.setObjectName("primaryButton")
        self.convert_btn.setCursor(Qt.PointingHandCursor)
        self.convert_btn.clicked.connect(lambda: self.start_requested.emit(self.mode))
        rl.addWidget(self.convert_btn)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.hide()
        rl.addWidget(self.progress)
        status_row = QHBoxLayout()
        self.status = QLabel("Choose your files, then press Convert to Text.")
        self.status.setObjectName("hint")
        self.status.setWordWrap(True)
        self.open_btn = QPushButton("Open output folder")
        self.open_btn.setObjectName("browseButton")
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.clicked.connect(self.open_output)
        self.open_btn.hide()
        status_row.addWidget(self.status, 1)
        status_row.addWidget(self.open_btn)
        rl.addLayout(status_row)
        col.addWidget(run)
        col.addStretch(1)
        self.apply_defaults()

    def _field_label(self, text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def _suggest_output(self, path):
        # Default the output to the input's folder until the user picks one
        if self.output.text() or not path:
            return
        folder = path if os.path.isdir(path) else os.path.dirname(path)
        if os.path.isdir(folder):
            self.output.setText(folder)

    def apply_defaults(self):
        index = self.language.findData(self.config.get("language"))
        if index >= 0:
            self.language.setCurrentIndex(index)
        if not self.output.text():
            self.output.setText(self.config.get("output_folder"))

    def options(self):
        return {
            "input": self.input.text(),
            "output_folder": self.output.text(),
            "plain_text": self.txt_chk.isChecked(),
            "msword": self.docx_chk.isChecked(),
            "single_file": self.single_chk.isChecked() if OCR_MODES[self.mode]["layout"] else True,
            "per_page": self.per_page_chk.isChecked() if OCR_MODES[self.mode]["layout"] else False,
            "language": self.language.currentData(),
        }

    def validate(self):
        """Return an error message, or None when the options are usable."""
        o = self.options()
        if not o["input"]:
            return OCR_MODES[self.mode]["missing_input"]
        if self.mode == "batch":
            if not os.path.isdir(o["input"]):
                return "The input folder doesn't exist."
        elif not os.path.isfile(o["input"]):
            return "The input file doesn't exist."
        if not o["output_folder"]:
            return "Choose a folder to save the results to."
        if not os.path.isdir(o["output_folder"]):
            return "The output folder doesn't exist."
        if not (o["plain_text"] or o["msword"]):
            return "Choose at least one output format."
        if not (o["single_file"] or o["per_page"]):
            return "Choose at least one output layout."
        return None

    def set_running(self, running):
        for w in (self.input, self.output, self.txt_chk, self.docx_chk,
                  self.single_chk, self.per_page_chk, self.language):
            w.setEnabled(not running)
        self.convert_btn.setEnabled(not running)
        self.convert_btn.setText("Converting..." if running else "Convert to Text")
        if running:
            self.progress.setValue(0)
            self.progress.show()
            self.open_btn.hide()

    def set_progress(self, value):
        self.progress.setValue(max(0, min(100, value)))

    def set_status(self, text, kind="hint"):
        self.status.setText(text)
        self.status.setObjectName(kind)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def finished(self, ok, message):
        self.set_running(False)
        self.set_status(message, "statusOk" if ok else "statusError")
        if ok:
            self.progress.setValue(100)
            self.open_btn.show()
        else:
            self.progress.hide()

    def open_output(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.output.text()))


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class SettingsPage(ScrollPage):
    theme_changed = Signal(str)
    settings_changed = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        col = self.column
        col.addLayout(header("Settings", "Changes are saved automatically."))

        # Appearance
        appearance, al = card("Appearance")
        al.addWidget(self._label("Theme"))
        self.theme = QComboBox()
        self.theme.addItem("Dark", "dark")
        self.theme.addItem("Light", "light")
        self.theme.setCurrentIndex(max(0, self.theme.findData(config.get("theme"))))
        self.theme.setMaximumWidth(260)
        self.theme.currentIndexChanged.connect(self._theme_changed)
        al.addWidget(self.theme)
        col.addWidget(appearance)

        # OCR defaults
        defaults, dl = card("OCR defaults")
        dl.addWidget(self._label("Default output folder"))
        self.output = PathField("Same folder as the input file")
        self.output.setText(config.get("output_folder"))
        self.output.changed.connect(lambda v: self._save("output_folder", v.strip()))
        dl.addWidget(self.output)

        row = QGridLayout()
        row.setHorizontalSpacing(30)
        row.setVerticalSpacing(8)
        row.addWidget(self._label("Default document language"), 0, 0)
        self.language = QComboBox()
        for name, code in LANGUAGES:
            self.language.addItem(name, code)
        self.language.setCurrentIndex(max(0, self.language.findData(config.get("language"))))
        self.language.setMinimumWidth(220)
        self.language.currentIndexChanged.connect(lambda: self._save("language", self.language.currentData()))
        row.addWidget(self.language, 1, 0)

        row.addWidget(self._label("PDF scan resolution"), 0, 1)
        self.dpi = QComboBox()
        for dpi in DPI_CHOICES:
            self.dpi.addItem(f"{dpi} DPI", dpi)
        if self.dpi.findData(config.get("dpi")) < 0:
            self.dpi.addItem(f"{config.get('dpi')} DPI", config.get("dpi"))
        self.dpi.setCurrentIndex(self.dpi.findData(config.get("dpi")))
        self.dpi.setMinimumWidth(160)
        self.dpi.currentIndexChanged.connect(lambda: self._save("dpi", self.dpi.currentData()))
        row.addWidget(self.dpi, 1, 1)
        row.setColumnStretch(2, 1)
        dl.addLayout(row)
        hint = QLabel("Higher resolution gives better accuracy on small print but is slower. 300 is a good default.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        dl.addWidget(hint)
        col.addWidget(defaults)

        # External tools
        tools, tl = card("OCR tools")
        tl.addWidget(self._label("Tesseract program (leave empty to use the built-in one)"))
        self.tesseract = PathField("e.g. C:\\Program Files\\Tesseract-OCR\\tesseract.exe", "exe")
        self.tesseract.setText(config.get("tesseract_cmd"))
        self.tesseract.edit.editingFinished.connect(self._tools_changed)
        self.tesseract.button.clicked.connect(self._tools_changed)
        tl.addWidget(self.tesseract)
        tl.addWidget(self._label("Poppler bin folder, for reading PDFs (leave empty to use the built-in one)"))
        self.poppler = PathField("e.g. C:\\Program Files\\poppler\\Library\\bin")
        self.poppler.setText(config.get("poppler_path"))
        self.poppler.edit.editingFinished.connect(self._tools_changed)
        self.poppler.button.clicked.connect(self._tools_changed)
        tl.addWidget(self.poppler)
        self.tool_status = QVBoxLayout()
        tl.addLayout(self.tool_status)
        check_btn = QPushButton("Check again")
        check_btn.setObjectName("browseButton")
        check_btn.setCursor(Qt.PointingHandCursor)
        check_btn.clicked.connect(self.refresh_status)
        tl.addWidget(check_btn, 0, Qt.AlignLeft)
        col.addWidget(tools)

        # About
        about, abl = card("About")
        text = QLabel(
            f"<b>{APP_NAME}</b> v{APP_VERSION} by Ehsan Aliverdi<br>"
            "Text recognition by Tesseract OCR. Interface based on PyDracula by Wanderson M. Pimenta; "
            "OCR pipeline based on FarsiOCR by Sajedeh Tafazzoli. Both MIT licensed.")
        text.setWordWrap(True)
        text.setObjectName("hint")
        abl.addWidget(text)
        col.addWidget(about)
        col.addStretch(1)
        self.refresh_status()

    def _label(self, text):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def _save(self, key, value):
        self.config.set(key, value)
        self.settings_changed.emit()

    def _theme_changed(self):
        theme = self.theme.currentData()
        self.config.set("theme", theme)
        self.theme_changed.emit(theme)

    def _tools_changed(self):
        self.config.set("tesseract_cmd", self.tesseract.text())
        self.config.set("poppler_path", self.poppler.text())
        self.refresh_status()
        self.settings_changed.emit()

    def refresh_status(self):
        while self.tool_status.count():
            item = self.tool_status.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        tess_ok, tess_msg = check_tesseract()
        self.tool_status.addWidget(status_label(tess_ok, tess_msg))
        if tess_ok:
            self.tool_status.addWidget(status_label(*check_language(self.config.get("language"))))
        self.tool_status.addWidget(status_label(*check_poppler(self.config.poppler_path())))
