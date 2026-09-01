import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from main import process_pdf
from logger_engine import log_info, log_error, get_log_path
from paths import resource_path, bundled_asset_path

class AppWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        # ------------ Window Basic Settings ------------
        self.setWindowTitle("BSP Generator – Kanoo Travel")
        self.setGeometry(300, 120, 700, 520)
        self.setStyleSheet("background-color: black;")

        # App icon
        self.setWindowIcon(QtGui.QIcon(bundled_asset_path("assets", "icon.ico")))

        # Variables to store selections
        self.selected_pdf = None
        self.output_folder = None

        # ------------ Main Layout ------------
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------ Company Logo ------------
        logo_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(bundled_asset_path("assets", "logo.png"))
        pixmap = pixmap.scaledToWidth(140, QtCore.Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(logo_label)

        # ------------ Buttons Layout ------------
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(QtCore.Qt.AlignCenter)

        button_style = """
        QPushButton {
            background-color: #256DFF;
            color: white;
            font-size: 18px;
            padding: 12px;
            border-radius: 12px;
            width: 260px;
        }
        QPushButton:hover {
            background-color: #144FCC;
        }
        """

        # ----- Select PDF -----
        self.btn_select_pdf = QtWidgets.QPushButton("Select BSP PDF")
        self.btn_select_pdf.setStyleSheet(button_style)
        self.btn_select_pdf.clicked.connect(self.select_pdf)
        btn_layout.addWidget(self.btn_select_pdf)

        # ----- Select Output Folder -----
        self.btn_output_folder = QtWidgets.QPushButton("Select Output Folder")
        self.btn_output_folder.setStyleSheet(button_style)
        self.btn_output_folder.clicked.connect(self.select_output_folder)
        btn_layout.addWidget(self.btn_output_folder)

        # ----- Convert Button -----
        self.btn_convert = QtWidgets.QPushButton("Convert to Excel (EGP)")
        self.btn_convert.setStyleSheet(button_style)
        self.btn_convert.clicked.connect(self.convert_file)
        btn_layout.addWidget(self.btn_convert)

        # ----- View Log -----
        self.btn_log = QtWidgets.QPushButton("View Log")
        self.btn_log.setStyleSheet(button_style)
        self.btn_log.clicked.connect(self.open_log)
        btn_layout.addWidget(self.btn_log)

        layout.addLayout(btn_layout)

        # ------------ Status Label ------------
        self.status = QtWidgets.QLabel("Ready")
        self.status.setStyleSheet("color: red; font-size: 18px;")
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status)

        self.setLayout(layout)

    # ----------------------------------------------------
    #                 Button Functions
    # ----------------------------------------------------

    def select_pdf(self):
        pdf, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select BSP PDF", "", "PDF Files (*.pdf)"
        )
        if pdf:
            self.selected_pdf = pdf
            self.status.setText("PDF Selected ✅")
            log_info(f"Selected PDF: {pdf}")

    def select_output_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Folder"
        )
        if folder:
            self.output_folder = folder
            self.status.setText("Output Folder Selected ✅")
            log_info(f"Selected Output Folder: {folder}")

    def convert_file(self):
        if not self.selected_pdf:
            self.status.setText("❌ No PDF selected!")
            return

        if not self.output_folder:
            self.status.setText("❌ No Output Folder selected!")
            return

        self.status.setText("Processing... ⏳")
        QtWidgets.QApplication.processEvents()

        try:
            output = process_pdf(self.selected_pdf, self.output_folder)
        except Exception as e:
            log_error(f"Unhandled GUI error during conversion: {e}")
            output = None

        if output:
            self.status.setText(f"✅ Done: {output}")
            log_info(f"Finished Output: {output}")
        else:
            self.status.setText("❌ Conversion Failed — راجع الـ View Log لمعرفة السبب")

    def open_log(self):
        log_path = get_log_path()
        try:
            os.startfile(log_path)
        except Exception as e:
            self.status.setText(f"Cannot open log file: {e} ({log_path})")
