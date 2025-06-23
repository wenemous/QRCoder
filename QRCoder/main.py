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


class QRCodeGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор QR-кодов")
        self.setMinimumSize(400, 500)
        self.current_qr_image = None

        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout()

        # Поле ввода
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите текст или URL...")
        layout.addWidget(self.input_field)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Сгенерировать")
        self.generate_btn.clicked.connect(self.generate_qr)
        buttons_layout.addWidget(self.generate_btn)

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_qr)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)

        self.print_btn = QPushButton("Печать")
        self.print_btn.clicked.connect(self.print_qr)
        self.print_btn.setEnabled(False)
        buttons_layout.addWidget(self.print_btn)

        layout.addLayout(buttons_layout)

        # Область отображения QR-кода
        self.qr_display = QLabel()
        self.qr_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_display.setText("QR-код появится здесь")
        self.qr_display.setMinimumSize(300, 300)
        layout.addWidget(self.qr_display)

        self.setLayout(layout)

    def generate_qr(self):
        """Генерация QR-кода из введенного текста"""
        text = self.input_field.text().strip()

        if not text:
            self.show_error("Ошибка", "Пожалуйста, введите текст для генерации QR-кода")
            return

        try:
            # Создаем QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            # Генерируем изображение
            img = qr.make_image(fill_color="black", back_color="white")
            self.current_qr_image = img

            # Отображаем QR-код
            self.display_qr_code(img)

            # Активируем кнопки
            self.save_btn.setEnabled(True)
            self.print_btn.setEnabled(True)

        except Exception as e:
            self.show_error("Ошибка генерации", f"Не удалось сгенерировать QR-код: {str(e)}")

    def display_qr_code(self, img):
        """Отображение QR-кода в интерфейсе"""
        # Конвертируем PIL Image в QPixmap
        qimage = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        # Масштабируем с сохранением пропорций
        scaled_pixmap = pixmap.scaled(
            self.qr_display.width() - 20,
            self.qr_display.height() - 20,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.qr_display.setPixmap(scaled_pixmap)

    def save_qr(self):
        """Сохранение QR-кода в файл"""
        if not self.current_qr_image:
            return

        default_name = "qr_code.png"
        if self.input_field.text().strip():
            # Создаем имя файла на основе текста (с ограничением длины и заменой спецсимволов)
            text = self.input_field.text()[:30]
            text = "".join(c if c.isalnum() else "_" for c in text)
            default_name = f"qr_{text}.png"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить QR-код",
            os.path.join(os.getcwd(), default_name),
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)"
        )

        if file_path:
            try:
                self.current_qr_image.save(file_path)
                QMessageBox.information(
                    self,
                    "Сохранено",
                    f"QR-код успешно сохранен как:\n{file_path}"
                )
            except Exception as e:
                self.show_error("Ошибка сохранения", f"Не удалось сохранить файл: {str(e)}")

    def print_qr(self):
        """Печать QR-кода через системный диалог печати"""
        if not self.current_qr_image:
            return

        # Создаем временный файл
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "temp_qr_print.png")

        try:
            # Сохраняем QR-код во временный файл
            self.current_qr_image.save(temp_path)

            # Открываем диалог печати (Windows)
            if sys.platform == "win32":
                subprocess.run([
                    "rundll32.exe",
                    "shell32.dll,PrintTo",
                    temp_path,
                    ""
                ], check=True)
            else:
                # Для других ОС можно использовать альтернативные методы
                QMessageBox.information(
                    self,
                    "Печать",
                    "Функция печати доступна только в Windows. "
                    "Сохраните QR-код и распечатайте его вручную."
                )

        except Exception as e:
            self.show_error("Ошибка печати", f"Не удалось выполнить печать: {str(e)}")
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def show_error(self, title, message):
        """Показ сообщения об ошибке"""
        QMessageBox.critical(self, title, message)

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)
        if self.current_qr_image:
            self.display_qr_code(self.current_qr_image)


def main():
    app = QApplication(sys.argv)

    # Настройка стиля приложения
    app.setStyle("Fusion")

    generator = QRCodeGenerator()
    generator.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()