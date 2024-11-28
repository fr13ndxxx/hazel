import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLineEdit, QLabel, QComboBox, QMessageBox, QSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from data_parser import DataParser
from validator import Validator
import os
import logging
import xml.etree.ElementTree as ET
import subprocess
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FeedErrorCorrectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Feed Error Correction')
        self.setGeometry(100, 100, 800, 600)

        # Set font
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # File selection
        self.file_button = QPushButton('Выбрать файл')
        self.file_button.setToolTip('Выберите файл для анализа')
        self.file_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.file_button)

        # Field selector and add button
        self.field_selector = QComboBox()
        self.field_selector.setToolTip('Выберите поле для добавления')
        self.layout.addWidget(self.field_selector)

        add_field_button = QPushButton('Добавить выбранное поле')
        add_field_button.setToolTip('Добавить выбранное поле для валидации')
        add_field_button.clicked.connect(self.add_field_input)
        self.layout.addWidget(add_field_button)

        # Process button
        self.process_button = QPushButton('Обработать файл')
        self.process_button.setToolTip('Начать обработку и валидацию файла')
        self.process_button.clicked.connect(self.process_file)
        self.layout.addWidget(self.process_button)

        # Field inputs
        self.field_layout = QVBoxLayout()
        self.layout.addLayout(self.field_layout)

        # Store selected file path and rules
        self.selected_file = None
        self.rules = {}

    def select_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Выберите файл', '', 'Data Files (*.csv *.xlsx *.xml *.json);;All Files (*)', options=options)
        if file_name:
            self.selected_file = file_name
            logging.info(f'Selected file: {file_name}')

            # Parse the file
            data = DataParser.parse_file(self.selected_file)
            logging.info(f'Parsed file: {self.selected_file}')

            # Populate field selector with columns from the file
            self.field_selector.clear()
            self.field_selector.addItems(data.columns)

    def add_field_input(self):
        selected_column = self.field_selector.currentText()

        # Check for duplicate fields
        for i in range(self.field_layout.count()):
            field_widget = self.field_layout.itemAt(i).widget()
            field_name_combo = field_widget.layout().itemAt(0).widget()
            if field_name_combo.currentText() == selected_column:
                QMessageBox.warning(self, 'Дубликат поля', f'Поле с названием {selected_column} уже существует.')
                return

        field_widget = QWidget()
        field_layout = QVBoxLayout()
        field_widget.setLayout(field_layout)

        # Determine data type
        data_type = 'СТРОКА'  # Default to STRING for manual addition

        field_name_combo = QComboBox()
        field_name_combo.addItems([selected_column])
        field_name_combo.setCurrentText(selected_column)
        field_name_combo.setToolTip('Выберите название поля для проверки')
        field_layout.addWidget(field_name_combo)

        # Validator configuration using SpinBoxes, ComboBoxes, and LineEdits
        validator_layout = QVBoxLayout()

        # Type selection
        type_label = QLabel('Тип данных')
        validator_layout.addWidget(type_label)
        type_combo = QComboBox()
        type_combo.addItems(['ЦЕЛОЕ', 'ВЕЩЕСТВЕННОЕ', 'СТРОКА', 'ДАТА'])
        validator_layout.addWidget(type_combo)

        # Min and Max values for numeric types
        min_label = QLabel('Минимальное значение')
        validator_layout.addWidget(min_label)
        min_spinbox = QSpinBox()
        min_spinbox.setMinimum(-1000000)
        min_spinbox.setMaximum(1000000)
        validator_layout.addWidget(min_spinbox)

        max_label = QLabel('Максимальное значение')
        validator_layout.addWidget(max_label)
        max_spinbox = QSpinBox()
        max_spinbox.setMinimum(-1000000)
        max_spinbox.setMaximum(1000000)
        validator_layout.addWidget(max_spinbox)

        # Max length for string type
        max_length_label = QLabel('Максимальная длина')
        validator_layout.addWidget(max_length_label)
        max_length_spinbox = QSpinBox()
        max_length_spinbox.setMinimum(1)
        max_length_spinbox.setMaximum(10000)
        validator_layout.addWidget(max_length_spinbox)

        # Format for date type
        date_format_label = QLabel('Формат даты')
        validator_layout.addWidget(date_format_label)
        date_format_input = QLineEdit('YYYY-MM-DD')
        validator_layout.addWidget(date_format_input)

        # Connect type selection to visibility logic
        def update_visibility():
            if type_combo.currentText() in ['ЦЕЛОЕ', 'ВЕЩЕСТВЕННОЕ']:
                min_spinbox.setVisible(True)
                max_spinbox.setVisible(True)
                max_length_spinbox.setVisible(False)
                date_format_input.setVisible(False)
            elif type_combo.currentText() == 'СТРОКА':
                min_spinbox.setVisible(False)
                max_spinbox.setVisible(False)
                max_length_spinbox.setVisible(True)
                date_format_input.setVisible(False)
            elif type_combo.currentText() == 'ДАТА':
                min_spinbox.setVisible(False)
                max_spinbox.setVisible(False)
                max_length_spinbox.setVisible(False)
                date_format_input.setVisible(True)

        type_combo.currentIndexChanged.connect(update_visibility)
        update_visibility()

        field_layout.addLayout(validator_layout)

        default_value_input = QLineEdit()
        default_value_input.setPlaceholderText('Стандартное значение')
        default_value_input.setToolTip('Введите стандартное значение для исправления')
        field_layout.addWidget(default_value_input)

        # Add remove button
        remove_button = QPushButton('Удалить поле')
        remove_button.setToolTip('Удалить это поле')
        remove_button.clicked.connect(lambda: self.remove_field_input(field_widget))
        field_layout.addWidget(remove_button)

        self.field_layout.addWidget(field_widget)

    def remove_field_input(self, field_widget):
        # Properly remove the field widget from the layout
        for i in range(self.field_layout.count()):
            item = self.field_layout.itemAt(i)
            if item.widget() == field_widget:
                # Remove the widget and delete it
                self.field_layout.takeAt(i)
                field_widget.deleteLater()
                break

    def process_file(self):
        if not self.selected_file:
            logging.warning('No file selected!')
            return

        # Collect rules from the UI
        self.rules = self.collect_rules()
        logging.info(f'Collected rules: {self.rules}')

        # Parse the file
        data = DataParser.parse_file(self.selected_file)
        logging.info(f'Parsed file: {self.selected_file}')

        # Validate the data
        validator = Validator(self.rules)
        errors = validator.validate(data)

        # Output errors
        if errors:
            for error in errors:
                index, field, value, rule = error
                logging.error(f'Error in row {index}, field {field}: {value} does not match rule {rule}')

            # Ask user if they want to correct errors
            reply = QMessageBox.question(self, 'Correct Errors', 'Do you want to correct the errors automatically?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.correct_errors(data, errors)
            else:
                self.manual_correction(data, errors)
        else:
            logging.info('No errors found!')

    def is_date(self, string):
        try:
            pd.to_datetime(string)
            return True
        except ValueError:
            return False

    def correct_errors(self, data, errors):
        for error in errors:
            index, field, value, rule = error
            # Use default value for correction
            default_value = rule.get('default', '')
            if rule['type'] == 'ЦЕЛОЕ':
                try:
                    data.at[index, field] = int(default_value) if default_value else 0
                except ValueError:
                    logging.error(f'Invalid default value for INTEGER: {default_value}')
                    data.at[index, field] = 0
            elif rule['type'] == 'ВЕЩЕСТВЕННОЕ':
                try:
                    data.at[index, field] = float(default_value) if default_value else 0.0
                except ValueError:
                    logging.error(f'Invalid default value for FLOAT: {default_value}')
                    data.at[index, field] = 0.0
            elif rule['type'] == 'СТРОКА':
                data.at[index, field] = default_value if default_value else ''

        # Save corrected file
        base, ext = os.path.splitext(self.selected_file)
        corrected_file = f'{base}_new{ext}'
        if ext == '.csv':
            data.to_csv(corrected_file, index=False)
        elif ext == '.xlsx':
            data.to_excel(corrected_file, index=False)
        elif ext == '.json':
            data.to_json(corrected_file, orient='records', lines=True)
        elif ext == '.xml':
            self.save_xml(data, corrected_file)

        logging.info(f'Corrected file saved as: {corrected_file}')

    def manual_correction(self, data, errors):
        # Highlight errors in the data
        for error in errors:
            index, field, value, rule = error
            data.at[index, field] = f'№-№-№-№-№-№-№{value}№-№-№-№-№-№-№'

        # Save the highlighted file as a temporary text file
        temp_file = 'temp_correction.txt'
        data.to_csv(temp_file, index=False, sep='\t')

        # Open the file in the default text editor
        subprocess.run(['notepad.exe', temp_file])

    def save_xml(self, dataframe, file_path):
        root = ET.Element('products')
        for _, row in dataframe.iterrows():
            product_elem = ET.SubElement(root, 'product')
            for field in dataframe.columns:
                field_elem = ET.SubElement(product_elem, field)
                field_elem.text = str(row[field])
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

    def collect_rules(self):
        rules = {}
        for i in range(self.field_layout.count()):
            field_widget = self.field_layout.itemAt(i).widget()
            field_name = field_widget.layout().itemAt(0).widget().currentText()
            validator_layout = field_widget.layout().itemAt(1)
            type_combo = validator_layout.itemAt(1).widget()
            min_spinbox = validator_layout.itemAt(3).widget()
            max_spinbox = validator_layout.itemAt(5).widget()
            max_length_spinbox = validator_layout.itemAt(7).widget()
            date_format_input = validator_layout.itemAt(9).widget()
            default_value_input = field_widget.layout().itemAt(2).widget()
            rules[field_name] = {
                'type': type_combo.currentText(),
                'min': min_spinbox.value(),
                'max': max_spinbox.value(),
                'max_length': max_length_spinbox.value(),
                'date_format': date_format_input.text(),
                'default': default_value_input.text()
            }
        return rules

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FeedErrorCorrectionApp()
    window.show()
    sys.exit(app.exec_())
