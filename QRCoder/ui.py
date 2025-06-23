from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import qrcode
from PIL.ImageQt import ImageQt
import os


class QRGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор QR-кодов")
        self.setFixedSize(400, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.init_ui()
        self.current_qr_image = None

    def init_ui(self):
        # Поле ввода
        self.input_label = QLabel("Введите текст или URL:")
        self.layout.addWidget(self.input_label)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Например: https://example.com")
        self.layout.addWidget(self.text_input)

        # Кнопка генерации
        self.generate_btn = QPushButton("Сгенерировать QR-код")
        self.generate_btn.clicked.connect(self.generate_qr)
        self.layout.addWidget(self.generate_btn)

        # Область для QR-кода
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setText("Здесь появится ваш QR-код")
        self.qr_label.setFixedSize(300, 300)
        self.layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        # Кнопки действий
        self.buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_qr)
        self.save_btn.setEnabled(False)
        self.buttons_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_all)
        self.buttons_layout.addWidget(self.clear_btn)

        self.layout.addLayout(self.buttons_layout)

    def generate_qr(self):
        text = self.text_input.text().strip()
        if not text:
            self.show_error("Пожалуйста, введите текст для генерации QR-кода")
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

            img = qr.make_image(fill_color="black", back_color="white")
            self.current_qr_image = img

            # Отображаем изображение
            qim = ImageQt(img)
            pixmap = QPixmap.fromImage(qim)
            self.qr_label.setPixmap(
                pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.save_btn.setEnabled(True)

        except Exception as e:
            self.show_error(f"Ошибка при генерации QR-кода: {str(e)}")

    def save_qr(self):
        if not self.current_qr_image:
            return

        default_name = "qr_code.png"
        if self.text_input.text().strip():
            default_name = f"qr_{self.text_input.text()[:20]}.png".replace("/", "_")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить QR-код",
            os.path.join(os.getcwd(), default_name),
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;All Files (*)"
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
                self.show_error(f"Ошибка при сохранении: {str(e)}")

    def clear_all(self):
        self.text_input.clear()
        self.qr_label.clear()
        self.qr_label.setText("Здесь появится ваш QR-код")
        self.save_btn.setEnabled(False)
        self.current_qr_image = None

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)