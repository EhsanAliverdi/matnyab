# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import platform
from PySide6 import QtWidgets
import threading
import traceback
import hashlib
import logging
 

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from modules.OCR.src.ocr import  ocr
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.threadpool = QThreadPool()
        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Matnyab"
        description = "Matnyab - Persian OCR"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_ocr.clicked.connect(self.buttonClick)
        widgets.btn_settings.clicked.connect(self.buttonClick)

        #Custom Buttons
        widgets.btn_pdf_ocr.clicked.connect(self.buttonClick)
        widgets.btn_image_ocr.clicked.connect(self.buttonClick)
        widgets.btn_batch_ocr.clicked.connect(self.buttonClick)
        
        widgets.ocr_batch_select_input_folder_btn.clicked.connect(self.buttonClick)
        widgets.ocr_batch_select_output_folder_btn.clicked.connect(self.buttonClick)
        widgets.ocr_batch_convert_btn.clicked.connect(lambda: self.start_ocr_process('BATCH'))

        widgets.ocr_image_select_input_file_btn.clicked.connect(self.buttonClick)
        widgets.ocr_image_select_output_folder_btn.clicked.connect(self.buttonClick)
        widgets.ocr_image_convert_btn.clicked.connect(lambda: self.start_ocr_process('IMAGE'))

        widgets.ocr_pdf_select_input_file_btn.clicked.connect(self.buttonClick)
        widgets.ocr_pdf_select_output_folder_btn.clicked.connect(self.buttonClick)
        widgets.ocr_pdf_convert_btn.clicked.connect(lambda: self.start_ocr_process('PDF'))

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, False)
        # widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        # widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, False)
        #widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))



        # SHOW OCR PAGE
        if btnName == "btn_ocr":
            widgets.stackedWidget.setCurrentWidget(widgets.ocr_home_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU
       
        
        # SHOW OCR PAGE
        if btnName == "btn_settings":
            widgets.stackedWidget.setCurrentWidget(widgets.settings_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        
        # SHOW PDF OCR PAGE
        if btnName == "btn_pdf_ocr":
            widgets.stackedWidget.setCurrentWidget(widgets.ocr_pdf_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU
        
        # SHOW Image OCR PAGE
        if btnName == "btn_image_ocr":
            widgets.stackedWidget.setCurrentWidget(widgets.ocr_image_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU
        
        # SHOW Batch OCR PAGE
        if btnName == "btn_batch_ocr":
            widgets.stackedWidget.setCurrentWidget(widgets.ocr_batch_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU
        
        
        
        # ---------------- Batch OCR Page
        if btnName == "ocr_batch_select_input_folder_btn":
            folderpath = QtWidgets.QFileDialog.getExistingDirectory()
            if folderpath:
                widgets.ocr_batch_input_folder_txt.setText(folderpath)

        if btnName == "ocr_batch_select_output_folder_btn":
            folderpath = QtWidgets.QFileDialog.getExistingDirectory()
            if folderpath:
                widgets.ocr_batch_output_folder_txt.setText(folderpath)

        if btnName == "ocr_batch_convert_btn":
            #TODO Check data
            #TODO IF valid
            self.start_ocr_process("BATCH")
            #TODO Disable all menu during process
            #Create Stop Button
            
        # ---------------- Image OCR Page
        if btnName == "ocr_image_select_input_file_btn":
            SUPPORTED_IMG_FORMAT = ['.png', '.jpg', '.jpeg', '.tiff']
            _filter = 'Images ('
            for format in SUPPORTED_IMG_FORMAT:
                _filter += ' *' + format
            _filter += ')'
            file = QtWidgets.QFileDialog.getOpenFileName(filter=_filter)
            if file:
                widgets.ocr_image_input_file_txt.setText(str(file[0]).replace('\\', '/'))

        if btnName == "ocr_image_select_output_folder_btn":
            folderpath = QtWidgets.QFileDialog.getExistingDirectory()
            if folderpath:
                widgets.ocr_image_output_folder_txt.setText(folderpath)

        if btnName == "ocr_image_convert_btn":
            #TODO Check data
            #TODO IF valid
            self.start_ocr_process("IMAGE")
            #TODO Disable all menu during process
            #Create Stop Button
        
        # ---------------- PDF OCR Page
        if btnName == "ocr_pdf_select_input_file_btn":
            _filter = "PDF (*.pdf)"
            file = QtWidgets.QFileDialog.getOpenFileName(filter=_filter)
            if file:
                widgets.ocr_pdf_input_file_txt.setText(str(file[0]).replace('\\', '/'))

        if btnName == "ocr_pdf_select_output_folder_btn":
            folderpath = QtWidgets.QFileDialog.getExistingDirectory()
            if folderpath:
                widgets.ocr_pdf_output_folder_txt.setText(folderpath)

        if btnName == "ocr_pdf_convert_btn":
            #TODO Check data
            #TODO IF valid
            self.start_ocr_process("PDF")
            #TODO Disable all menu during process
            #Create Stop Button




           
            print(f"{str(folderpath)}")
            print("end!")

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        p = event.globalPosition()
        self.dragPos = p.toPoint()
        #self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
    
    
    
    
    def start_ocr_process(self,process_type: str):
        if process_type == "BATCH":
            input = widgets.ocr_batch_input_folder_txt.text()
            input_type = "FOLDER"
            output_folder = widgets.ocr_batch_output_folder_txt.text()
            single_file = widgets.ocr_batch_single_file_chk.isChecked()
            per_page_file = widgets.ocr_batch_per_page_chk.isChecked()
            ms_world_output = widgets.ocr_batch_single_file_chk.isChecked()
            plaind_text_output = widgets.ocr_batch_per_page_chk.isChecked()
            x = ocr (input,input_type, output_folder, single_file, per_page_file, ms_world_output, plaind_text_output)
            worker = Worker(x.main)  # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            # Execute
            self.threadpool.start(worker)
        if process_type == "IMAGE":
            input = widgets.ocr_image_input_file_txt.text()
            input_type = "FILE"
            output_folder = widgets.ocr_image_output_folder_txt.text()
            single_file = True
            per_page_file = False
            ms_world_output = widgets.ocr_image_msword_chk.isChecked()
            plaind_text_output = widgets.ocr_image_plain_text_chk.isChecked()
            x = ocr (input,input_type, output_folder, single_file, per_page_file, ms_world_output, plaind_text_output)
            worker = Worker(x.main)  # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            # Execute
            self.threadpool.start(worker)
        if process_type == "PDF":
            input = widgets.ocr_pdf_input_file_txt.text()
            input_type = "FILE"
            output_folder = widgets.ocr_pdf_output_folder_txt.text()
            single_file = True
            per_page_file = True
            ms_world_output = widgets.ocr_pdf_msword_chk.isChecked()
            plaind_text_output = widgets.ocr_pdf_plain_text_chk.isChecked()
            x = ocr (input,input_type, output_folder, single_file, per_page_file, ms_world_output, plaind_text_output)
            worker = Worker(x.main)  # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            # Execute
            self.threadpool.start(worker)
        
 
    def progress_fn(self, n):
        print("%d%% done" % n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())

