import sys
from PyQt5.QtWidgets import QApplication
import app.ui as ui

def main():
    app = QApplication(sys.argv)
    window = ui.ImageViewer()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
