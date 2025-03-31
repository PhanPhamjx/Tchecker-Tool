import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow
import os

def main():
    app = QApplication(sys.argv)
    
    # Thiết lập icon cho ứng dụng
    icon_path = os.path.join(os.path.dirname(__file__), "icon", "iconT.jpg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()