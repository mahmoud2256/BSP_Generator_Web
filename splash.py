from PyQt5 import QtWidgets, QtGui, QtCore
import time
from paths import resource_path, bundled_asset_path

class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):

        # Load company logo
        pixmap = QtGui.QPixmap(bundled_asset_path("assets", "logo.png"))
        pixmap = pixmap.scaled(
            340,
            180,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        # Initialize the splash screen
        super().__init__(pixmap)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setEnabled(False)

        # Add loading text
        self.loading = QtWidgets.QLabel(self)
        self.loading.setText("Loading BSP Generator Project…")
        self.loading.setStyleSheet("color: white; font-size: 14px;")
        self.loading.setAlignment(QtCore.Qt.AlignCenter)

        # Position loading text under logo
        self.loading.setGeometry(
            0,
            pixmap.height() - 30,
            pixmap.width(),
            30
        )

    def show_and_fade(self, duration=3):
        self.show()
        QtWidgets.QApplication.processEvents()
        time.sleep(duration)
