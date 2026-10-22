# ///////////////////////////////////////////////////////////////
#
# Matnyab - Persian (Farsi) OCR
#
# Window shell based on PyDracula by Wanderson M. Pimenta
# (Qt Designer and PySide6, MIT licensed).
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from modules.config import APP_NAME, APP_VERSION, AppConfig
from modules.pages import HomePage, OcrPage, SettingsPage, page_stylesheet
from modules.OCR.src.ocr import ocr
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

# Selected-menu highlight for each theme
MENU_SELECTED = {
    "dark": Settings.MENU_SELECTED_STYLESHEET,
    "light": """
    border-left: 22px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 rgba(255, 121, 198, 255), stop:0.5 rgba(85, 170, 255, 0));
    background-color: #67528c;
    """,
}

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.threadpool = QThreadPool()
        self.config = AppConfig()
        self.config.apply_tesseract_cmd()
        self.running_page = None

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        self.dark_stylesheet = widgets.styleSheet.styleSheet()

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        self.setWindowTitle(f"{APP_NAME} - Persian OCR")
        widgets.titleRightInfo.setText(f"{APP_NAME} - Persian OCR")
        widgets.version.setText(f"v{APP_VERSION}")

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # PAGES
        # ///////////////////////////////////////////////////////////////
        self.home_page = HomePage(self.config)
        self.home_page.navigate.connect(self.show_page)
        self.ocr_pages = {mode: OcrPage(mode, self.config) for mode in ("pdf", "image", "batch")}
        for page in self.ocr_pages.values():
            page.start_requested.connect(self.start_ocr_process)
        self.settings_page = SettingsPage(self.config)
        self.settings_page.theme_changed.connect(self.apply_theme)
        self.settings_page.settings_changed.connect(self.settings_changed)

        self.pages = {"home": self.home_page, **self.ocr_pages, "settings": self.settings_page}
        for page in self.pages.values():
            widgets.stackedWidget.addWidget(page)

        # LEFT MENU
        # ///////////////////////////////////////////////////////////////
        self.menu_buttons = {
            "home": widgets.btn_home,
            "pdf": widgets.btn_pdf,
            "image": widgets.btn_image,
            "batch": widgets.btn_batch,
            "settings": widgets.btn_settings,
        }
        for key, btn in self.menu_buttons.items():
            btn.clicked.connect(lambda checked=False, k=key: self.show_page(k))

        # THEME, THEN SHOW APP ON THE HOME PAGE
        # ///////////////////////////////////////////////////////////////
        self.current_page = "home"
        self.apply_theme(self.config.get("theme"))
        self.show_page("home")
        self.show()

    # NAVIGATION
    # ///////////////////////////////////////////////////////////////
    def show_page(self, key):
        self.current_page = key
        page = self.pages[key]
        widgets.stackedWidget.setCurrentWidget(page)
        # Pages that were hidden when the theme was set don't repolish on their own
        page.setStyleSheet(page_stylesheet(self.theme))
        for name, btn in self.menu_buttons.items():
            style = UIFunctions.deselectMenu(btn.styleSheet())
            btn.setStyleSheet(UIFunctions.selectMenu(style) if name == key else style)

    # THEMES
    # ///////////////////////////////////////////////////////////////
    def apply_theme(self, theme):
        for btn in self.menu_buttons.values():
            btn.setStyleSheet(UIFunctions.deselectMenu(btn.styleSheet()))
        Settings.MENU_SELECTED_STYLESHEET = MENU_SELECTED[theme]
        if theme == "light":
            UIFunctions.theme(self, os.path.join(BASE_DIR, "themes", "py_dracula_light.qss"), True)
        else:
            widgets.styleSheet.setStyleSheet(self.dark_stylesheet)
        self.theme = theme
        self.show_page(self.current_page)

    def settings_changed(self):
        self.home_page.refresh_status()
        for page in self.ocr_pages.values():
            page.apply_defaults()

    # MOUSE AND RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition().toPoint()

    # OCR
    # ///////////////////////////////////////////////////////////////
    def start_ocr_process(self, mode):
        page = self.ocr_pages[mode]
        if self.running_page is not None:
            QMessageBox.information(self, APP_NAME, "A conversion is already running. Please wait for it to finish.")
            return
        error = page.validate()
        if error:
            page.set_status(error, "statusError")
            return

        o = page.options()
        try:
            job = ocr(o["input"], "FOLDER" if mode == "batch" else "FILE", o["output_folder"],
                      single_file=o["single_file"], per_page_file=o["per_page"],
                      ms_world_output=o["msword"], plain_text_output=o["plain_text"],
                      langs=o["language"], dpi=self.config.get("dpi"),
                      poppler_path=self.config.poppler_path())
        except Exception as e:
            page.finished(False, f"Couldn't start: {e}")
            return

        self.running_page = page
        page.set_running(True)
        page.set_status("Starting...")
        worker = Worker(job.main)
        worker.signals.progress.connect(page.set_progress)
        worker.signals.status.connect(page.set_status)
        worker.signals.error.connect(self.ocr_failed)
        worker.signals.result.connect(self.ocr_succeeded)
        self.threadpool.start(worker)

    def ocr_succeeded(self, _result):
        page, self.running_page = self.running_page, None
        page.finished(True, "Done. Your files are in the output folder.")

    def ocr_failed(self, error):
        page, self.running_page = self.running_page, None
        _, value, _ = error
        page.finished(False, f"Conversion failed: {value}")


def run_self_test(input_path, report_path):
    """Convert one file without the window and write a report. Used to check release builds."""
    import json
    import tempfile
    from modules.config import check_language, check_poppler, check_tesseract

    config = AppConfig()
    config.apply_tesseract_cmd()
    report = {
        "tesseract": check_tesseract(),
        "language": check_language("fas"),
        "poppler": check_poppler(config.poppler_path()),
    }
    out = tempfile.mkdtemp(prefix="matnyab-selftest-")
    try:
        ocr(input_path, "FILE", out, single_file=True, per_page_file=False,
            ms_world_output=True, plain_text_output=True,
            langs="fas", dpi=config.get("dpi"), poppler_path=config.poppler_path()).main()
        report["outputs"] = sorted(os.listdir(out))
        texts = [f for f in report["outputs"] if f.endswith(".txt")]
        with open(os.path.join(out, texts[0]), encoding="utf-8") as f:
            report["text"] = f.read()
    except Exception as e:
        report["error"] = repr(e)
    report["ok"] = all(report[k][0] for k in ("tesseract", "language", "poppler")) and bool(report.get("text", "").strip())
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        i = sys.argv.index("--self-test")
        sys.exit(run_self_test(sys.argv[i + 1], sys.argv[i + 2]))

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon(os.path.join(BASE_DIR, "icon.ico")))
    window = MainWindow()
    sys.exit(app.exec())
