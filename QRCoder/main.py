from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import qrcode
from PIL.ImageQt import ImageQt
import sys


class QRCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор QR-кода")
        self.setGeometry(100, 100, 300, 400)

        self.layout = QVBoxLayout()

        self.label_instruction = QLabel("Введите текст для генерации QR-кода:")
        self.layout.addWidget(self.label_instruction)

        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)

        self.button_generate = QPushButton("Сгенерировать QR-код")
        self.button_generate.clicked.connect(self.generate_qrcode)
        self.layout.addWidget(self.button_generate)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.qr_label)

        self.setLayout(self.layout)

    def generate_qrcode(self):
        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите текст.")
            return

        # Генерируем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Конвертируем PIL Image в QPixmap для отображения в QLabel
        qt_image = ImageQt(img)
        pixmap = QPixmap.fromImage(qt_image)
        self.qr_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))


def main():
    app = QApplication(sys.argv)
    window = QRCodeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
