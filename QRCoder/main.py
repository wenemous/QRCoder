import sys
import os
import tempfile
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QSize
import qrcode
from PIL import Image


class QRCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор QR-кода")
        self.setGeometry(100, 100, 300, 450)

        self.layout = QVBoxLayout()

        self.label_instruction = QLabel("Введите текст для генерации QR-кода:")
        self.layout.addWidget(self.label_instruction)

        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)

        # Горизонтальный лэйаут для кнопок
        self.buttons_layout = QHBoxLayout()

        self.button_generate = QPushButton("Сгенерировать QR-код")
        self.button_generate.clicked.connect(self.generate_qrcode)
        self.buttons_layout.addWidget(self.button_generate)

        self.button_print = QPushButton("Печать QR-кода")
        self.button_print.clicked.connect(self.print_qrcode)
        self.button_print.setEnabled(False)  # Пока QR-код не сгенерирован, кнопка неактивна
        self.buttons_layout.addWidget(self.button_print)

        self.layout.addLayout(self.buttons_layout)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.qr_label)

        self.setLayout(self.layout)

        self.button_print_dialog = QPushButton("Печать с диалогом Windows")
        self.button_print_dialog.clicked.connect(self.print_qrcode_native_dialog)
        self.button_print_dialog.setEnabled(False)
        self.buttons_layout.addWidget(self.button_print_dialog)

        self.current_pixmap = None  # Для хранения текущего QR-кода

    def generate_qrcode(self):
        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите текст.")
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        qt_image = ImageQt(img)
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)

        self.qr_label.setPixmap(scaled_pixmap)
        self.current_pixmap = scaled_pixmap
        self.button_print.setEnabled(True)  # Активируем кнопку печати
        self.button_print_dialog.setEnabled(True)

    def print_qrcode_native_dialog(self):
        if self.current_pixmap is None:
            QMessageBox.warning(self, "Ошибка", "Сначала сгенерируйте QR-код.")
            return

        # Сохраняем текущий QR-код во временный PNG файл
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "temp_qrcode.png")
        self.current_pixmap.save(temp_path, "PNG")

        # Вызываем нативный диалог печати Windows через rundll32
        # Команда открывает диалог печати для указанного файла
        try:
            subprocess.run([
                "rundll32.exe",
                "shell32.dll,PrintTo",
                temp_path,
                # Можно указать имя принтера, но оставим пустым для выбора
                ""
            ], check=True)
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть диалог печати:\n{e}")
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.remove(temp_path)


def main():
    app = QApplication(sys.argv)
    window = QRCodeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
