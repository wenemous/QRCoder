import sys
import pandas as pd
import qrcode
from PyQt6.QtWidgets import (QApplication, QWidget, QTableView, QHeaderView,
                             QVBoxLayout, QPushButton, QFileDialog,
                             QAbstractItemView, QDialog, QLabel, QHBoxLayout,
                             QLineEdit, QInputDialog, QMessageBox)
from PyQt6.QtGui import (QStandardItemModel, QStandardItem, QPixmap, QIcon,
                             QPainter)
from PyQt6.QtCore import Qt
# from PyQt6.QtPrintSupport import QPrinter, QPrintDialog  # Remove Qt Print
import win32api
import win32print
import os

class QRDialog(QDialog):
    def __init__(self, qr_image_path, parent=None):  # Now takes image path
        super().__init__(parent)
        self.setWindowTitle("QRCoder")
        self.setWindowIcon(QIcon("qr_icon.png"))
        self.qr_image_path = qr_image_path  # Store the path
        self.qr_image = QPixmap(self.qr_image_path) # Load from file
        self.qr_label = QLabel()
        self.qr_label.setPixmap(self.qr_image)

        print_button = QPushButton("Печать QR-кода")
        print_button.clicked.connect(self.print_qr_code)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)

        hbox = QHBoxLayout()
        hbox.addWidget(print_button)
        hbox.addWidget(close_button)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.qr_label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def print_qr_code(self):
        try:
            win32api.ShellExecute(0, 'print', self.qr_image_path, f'/d:"{win32print.GetDefaultPrinter()}"', '.', 0)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка печати", f"Произошла ошибка при печати: {e}")


class ScanWindow(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Режим сканирования")
        self.setWindowIcon(QIcon("qr_icon.png"))
        self.main_window = main_window

        self.scan_mode = False
        self.scan_data = []
        self.expected_columns = ["Name", "Model", "SerialNum", "InventoryNum", "Employee", "ActDate", "Comment"]

        self.clear_table_button = QPushButton("Очистить таблицу")
        self.clear_table_button.clicked.connect(self.clear_table)
        self.clear_table_button.setEnabled(False)

        self.export_button = QPushButton("Экспорт таблицы")
        self.export_button.clicked.connect(self.export_table)
        self.export_button.setEnabled(False)

        self.scan_mode_button = QPushButton("Режим сканирования QR")
        self.scan_mode_button.clicked.connect(self.enter_scan_mode)

        self.exit_scan_mode_button = QPushButton("Выйти из режима сканирования")
        self.exit_scan_mode_button.clicked.connect(self.exit_scan_mode)
        self.exit_scan_mode_button.setEnabled(False)

        # Main layout
        main_layout = QVBoxLayout()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.scan_mode_button)
        button_layout.addWidget(self.exit_scan_mode_button)  # Added exit button
        button_layout.addWidget(self.clear_table_button)
        button_layout.addWidget(self.export_button)
        main_layout.addLayout(button_layout)

        # Input Line Edit
        self.input_line_edit = QLineEdit()
        self.input_line_edit.returnPressed.connect(self.process_scan_input)
        main_layout.addWidget(self.input_line_edit)

        # Table View
        self.scan_table_view = QTableView()
        self.scan_table_model = QStandardItemModel()
        self.scan_table_view.setModel(self.scan_table_model)
        self.scan_table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.scan_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.scan_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.scan_table_view)

        # Set main layout
        self.setLayout(main_layout)

    def enter_scan_mode(self):
        self.scan_mode = True
        self.scan_mode_button.setEnabled(False)
        self.exit_scan_mode_button.setEnabled(True) # enable exit button
        self.clear_table_button.setEnabled(True)
        self.export_button.setEnabled(True)

        self.scan_data = []
        self.df = None
        self.df = pd.DataFrame(columns=self.expected_columns)
        self.populate_table(df=self.df)
        QMessageBox.information(self, "Режим сканирования", "Вы вошли в режим сканирования QR-кодов. Вводите данные в формате 'Key:Value Key:Value ...' и нажимайте Enter.")

        self.input_line_edit.setFocus()

    def process_scan_input(self):
        if self.scan_mode: # Only process input if scan mode is active
            text = self.input_line_edit.text()
            self.input_line_edit.clear()
            self.input_line_edit.setFocus()

            if text:
                try:
                    data = {}
                    pairs = text.split()
                    for pair in pairs:
                        try:
                            key, value = pair.split(':', 1)
                            data[key.strip()] = value.strip()
                        except ValueError:
                            QMessageBox.warning(self, "Ошибка", f"Неверный формат пары: {pair}. Пропускается.")
                            continue

                    for col in self.expected_columns:
                        if col not in data:
                            data[col] = ""

                    ordered_data = {col: data.get(col, "") for col in self.expected_columns}
                    new_df = pd.DataFrame([ordered_data])
                    self.df = pd.concat([self.df, new_df], ignore_index=True)
                    self.populate_table(df=self.df)
                    self.show_qr_code(text)

                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Общая ошибка при обработке данных: {e}")

    def exit_scan_mode(self):
        self.scan_mode = False
        self.scan_mode_button.setEnabled(True)  # Re-enable the scan mode button
        self.exit_scan_mode_button.setEnabled(False) # disable exit button

        self.clear_table_button.setEnabled(False)
        self.export_button.setEnabled(False)
        QMessageBox.information(self, "Режим сканирования", "Вы вышли из режима сканирования.")

    def clear_table(self):
        reply = QMessageBox.question(self, 'Очистка таблицы', 'Вы уверены, что хотите очистить таблицу?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.scan_data = []
            self.df = None
            self.df = pd.DataFrame(columns=self.expected_columns)
            self.populate_table(df=self.df)

    def export_table(self):
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Экспорт таблицы", "Таблица пуста и нечего экспортировать.")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Сохранить таблицу как", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")

        if file_path:
            try:
                if file_path.endswith(".csv"):
                    self.df.to_csv(file_path, index=False, encoding='utf-8')
                    QMessageBox.information(self, "Экспорт таблицы", f"Таблица успешно экспортирована в {file_path}")
                elif file_path.endswith(".xlsx"):
                    self.df.to_excel(file_path, index=False)
                    QMessageBox.information(self, "Экспорт таблицы", f"Таблица успешно экспортирована в {file_path}")
                else:
                    QMessageBox.warning(self, "Экспорт таблицы", "Неподдерживаемый формат файла.  Пожалуйста, выберите .csv или .xlsx.")
            except Exception as e:
                QMessageBox.critical(self, "Экспорт таблицы", f"Ошибка при экспорте таблицы: {e}")

    def populate_table(self, df):
        self.scan_table_model.clear()
        if df is not None and not df.empty:
            self.scan_table_model.setRowCount(df.shape[0])
            self.scan_table_model.setColumnCount(df.shape[1])
            self.scan_table_model.setHorizontalHeaderLabels(df.columns)
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    item = QStandardItem(str(df.iloc[row, col]))
                    self.scan_table_model.setItem(row, col, item)
        else:
            self.scan_table_model.setRowCount(0)
            self.scan_table_model.setColumnCount(len(self.expected_columns))
            self.scan_table_model.setHorizontalHeaderLabels(self.expected_columns)

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
        img_path = "temp_qr.png"  # Save the QR code image to a file
        img.save(img_path)

        dialog = QRDialog(img_path, self) # Pass the image path
        dialog.exec()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QRCoder")
        self.setWindowIcon(QIcon("qr_icon.png"))
        self.setGeometry(100, 100, 800, 600)

        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_view.setModel(self.table_model)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.load_button = QPushButton("Выбрать таблицу")
        self.load_button.clicked.connect(self.load_xls)

        self.open_scan_window_button = QPushButton("Открыть окно сканирования")
        self.open_scan_window_button.clicked.connect(self.open_scan_window)


        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.open_scan_window_button)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        self.table_view.clicked.connect(self.row_selected)
        self.scan_window = None # Initialize ScanWindow as None

    def load_xls(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open XLS File", "", "XLS Files (*.xls *.xlsx)")
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.populate_table(df=self.df)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки файла: {e}")

    def populate_table(self, df):
        self.table_model.clear()
        if df is not None and not df.empty:
            self.table_model.setRowCount(df.shape[0])
            self.table_model.setColumnCount(df.shape[1])
            self.table_model.setHorizontalHeaderLabels(df.columns)
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    item = QStandardItem(str(df.iloc[row, col]))
                    self.table_model.setItem(row, col, item)
        else:
            self.table_model.setRowCount(0)
            self.table_model.setColumnCount(0)
            self.table_model.setHorizontalHeaderLabels([]) # no header if empty table

    def row_selected(self, index):
        row = index.row()
        data = self.df.iloc[row].to_dict()
        qr_text = self.format_qr_data(data)
        self.show_qr_code(qr_text)

    def format_qr_data(self, data):
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
        img_path = "temp_qr.png"  # Save the QR code image to a file
        img.save(img_path)

        dialog = QRDialog(img_path, self) # Pass the image path
        dialog.exec()

    def open_scan_window(self):
        if self.scan_window is None: # only one window at a time
            self.scan_window = ScanWindow(self) # Pass a reference to the main window
        self.scan_window.show() # open the dialog

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())