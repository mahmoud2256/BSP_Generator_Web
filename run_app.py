import sys
from PyQt5 import QtWidgets
from splash import SplashScreen
from gui import AppWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Show Splash Screen
    splash = SplashScreen()
    splash.show_and_fade(duration=3)  # 3 seconds

    # Start Main Window
    window = AppWindow()
    window.show()

    sys.exit(app.exec_())
