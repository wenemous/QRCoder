import sys
import pandas as pd
import qrcode
from PyQt6.QtWidgets import (QApplication, QWidget, QTableView, QHeaderView,
                             QVBoxLayout, QPushButton, QFileDialog,
                             QAbstractItemView, QDialog, QLabel, QHBoxLayout)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon
from PyQt6.QtCore import Qt

class QRDialog(QDialog):
    def __init__(self, qr_image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QRCoder")
        self.setWindowIcon(QIcon("qr_icon.png"))
        self.qr_label = QLabel()
        self.qr_label.setPixmap(qr_image)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)

        hbox = QHBoxLayout()
        hbox.addWidget(close_button)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.qr_label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QRCoder")
        self.setGeometry(100, 100, 800, 600)

        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_view.setModel(self.table_model)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Запретить редактирование
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # Выделять строки целиком
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # Растягивать колонки

        self.load_button = QPushButton("Выбрать таблицу")
        self.load_button.clicked.connect(self.load_xls)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        self.table_view.clicked.connect(self.row_selected)

    def load_xls(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open XLS File", "", "XLS Files (*.xls *.xlsx)")
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.populate_table()
            except Exception as e:
                print(f"Error loading file: {e}")

    def populate_table(self):
        self.table_model.clear()
        self.table_model.setRowCount(self.df.shape[0])
        self.table_model.setColumnCount(self.df.shape[1])
        self.table_model.setHorizontalHeaderLabels(self.df.columns)

        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                item = QStandardItem(str(self.df.iloc[row, col]))
                self.table_model.setItem(row, col, item)

    def row_selected(self, index):
        row = index.row()
        data = self.df.iloc[row].to_dict()
        qr_text = self.format_qr_data(data)
        self.show_qr_code(qr_text)

    def format_qr_data(self, data):
       # Преобразует данные строки в строку для QR-кода
        formatted_string = ""
        for key, value in data.items():
            formatted_string += f"{key}:{value}\n"
        return formatted_string

    def show_qr_code(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save("temp_qr.png")
        qr_image = QPixmap("temp_qr.png")

        dialog = QRDialog(qr_image, self)
        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
