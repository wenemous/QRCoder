import sys
import os
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout,
    QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import qrcode
from PIL import Image
import win32print
import win32ui
import win32con


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
        self.print_btn.clicked.connect(self.print_qr_native)
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
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            self.current_qr_image = img
            self.display_qr_code(img)
            self.save_btn.setEnabled(True)
            self.print_btn.setEnabled(True)

        except Exception as e:
            self.show_error("Ошибка генерации", f"Не удалось сгенерировать QR-код: {str(e)}")

    def display_qr_code(self, img):
        """Отображение QR-кода в интерфейсе"""
        qimage = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
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

    def print_qr_native(self):
        """Нативная печать через Windows API с обработкой отсутствия принтера"""
        if not self.current_qr_image:
            return

        try:
            # Проверка наличия принтеров
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            if not printers:
                self.show_error("Ошибка", "Не найдены принтеры. Подключите принтер и попробуйте снова.")
                return

            # Получаем дефолтный принтер или первый доступный
            try:
                printer_name = win32print.GetDefaultPrinter()
            except:
                printer_name = printers[0][2]  # Берем первый доступный принтер

            # Создаем временный BMP файл
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "temp_qr_print.bmp")
            self.current_qr_image.save(temp_path)

            # Открываем принтер
            hprinter = win32print.OpenPrinter(printer_name)
            try:
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(printer_name)
                hdc.StartDoc("QR Code Print")
                hdc.StartPage()

                # Загружаем изображение
                bmp = win32ui.CreateBitmap()
                bmp.LoadBitmap(temp_path)

                # Получаем размеры
                bmp_info = bmp.GetInfo()
                img_width = bmp_info['bmWidth']
                img_height = bmp_info['bmHeight']

                # Получаем размеры страницы
                printable_width = hdc.GetDeviceCaps(win32con.HORZRES)
                printable_height = hdc.GetDeviceCaps(win32con.VERTRES)

                # Масштабирование с сохранением пропорций
                scale = min(printable_width / img_width, printable_height / img_height) * 0.9
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)

                # Центрирование
                x_pos = (printable_width - new_width) // 2
                y_pos = (printable_height - new_height) // 2

                # Печать
                hdc.StretchBlt(
                    x_pos, y_pos, new_width, new_height,
                    bmp.GetHandle(),
                    0, 0, img_width, img_height,
                    win32con.SRCCOPY
                )

                hdc.EndPage()
                hdc.EndDoc()

                QMessageBox.information(
                    self,
                    "Печать",
                    f"QR-код отправлен на принтер:\n{printer_name}"
                )

            except Exception as e:
                self.show_error("Ошибка печати", f"Ошибка при печати: {str(e)}")
            finally:
                win32print.ClosePrinter(hprinter)
                hdc.DeleteDC()
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            self.show_error("Ошибка", f"Не удалось выполнить печать: {str(e)}")

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
    app.setStyle("Fusion")
    generator = QRCodeGenerator()
    generator.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()