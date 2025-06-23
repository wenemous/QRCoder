import sys
from PyQt5.QtWidgets import QApplication
from .ui import QRGeneratorWindow


def main():
    app = QApplication(sys.argv)

    # Настройка стиля
    app.setStyle('Fusion')

    window = QRGeneratorWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()