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

