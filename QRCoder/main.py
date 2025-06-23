from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import qrcode
from PIL.ImageQt import ImageQt
import sys

import win32print
import win32ui
import win32con
from PIL import Image, ImageWin


class QRCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор QR-кода")
        self.setGeometry(100, 100, 350, 450)

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

        self.button_print_native = QPushButton("Печать (Windows)")
        self.button_print_native.clicked.connect(self.print_qrcode_native)
        self.button_print_native.setEnabled(False)  # Пока QR-код не сгенерирован
        self.buttons_layout.addWidget(self.button_print_native)

        self.layout.addLayout(self.buttons_layout)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.qr_label)

        self.setLayout(self.layout)

        self.current_pixmap = None  # Для хранения текущего QR-кода

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
        scaled_pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)

        self.qr_label.setPixmap(scaled_pixmap)
        self.current_pixmap = scaled_pixmap
        self.button_print_native.setEnabled(True)  # Активируем кнопку печати

    def print_qrcode_native(self):
        if self.current_pixmap is None:
            QMessageBox.warning(self, "Ошибка", "Сначала сгенерируйте QR-код.")
            return

        # Конвертируем QPixmap обратно в PIL Image
        qimage = self.current_pixmap.toImage()
        qimage = qimage.convertToFormat(4)  # QImage.Format_RGBA8888 = 4
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())
        img = Image.frombuffer("RGBA", (width, height), ptr, "raw", "RGBA", 0, 1)

        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)

            printable_area = hDC.GetDeviceCaps(win32con.HORZRES), hDC.GetDeviceCaps(win32con.VERTRES)
            printer_size = hDC.GetDeviceCaps(win32con.PHYSICALWIDTH), hDC.GetDeviceCaps(win32con.PHYSICALHEIGHT)
            printer_margins = hDC.GetDeviceCaps(win32con.PHYSICALOFFSETX), hDC.GetDeviceCaps(win32con.PHYSICALOFFSETY)

            # Масштабируем изображение под printable_area
            img_ratio = img.width / img.height
            area_ratio = printable_area[0] / printable_area[1]

            if img_ratio > area_ratio:
                scaled_width = printable_area[0]
                scaled_height = int(scaled_width / img_ratio)
            else:
                scaled_height = printable_area[1]
                scaled_width = int(scaled_height * img_ratio)

            hDC.StartDoc("QR Code Print")
            hDC.StartPage()

            dib = ImageWin.Dib(img)
            x = int((printable_area[0] - scaled_width) / 2)
            y = int((printable_area[1] - scaled_height) / 2)
            dib.draw(hDC.GetHandleOutput(), (x, y, x + scaled_width, y + scaled_height))

            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()
        finally:
            win32print.ClosePrinter(hPrinter)


def main():
    app = QApplication(sys.argv)
    window = QRCodeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
