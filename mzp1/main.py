import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLineEdit, QComboBox, QPushButton,
                           QScrollArea, QLabel, QSpinBox, QDoubleSpinBox,
                           QGridLayout, QFrame, QDateEdit, QMessageBox, QSplitter,
                           QMenu, QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPalette, QColor

class ConditionWidget(QFrame):
    def __init__(self, field_type, condition_type, parent=None):
        super().__init__(parent)
        self.setObjectName("conditionFrame")
        self.field_type = field_type
        self.condition_type = condition_type
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
        # Название условия
        condition_label = QLabel(condition_type)
        condition_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(condition_label)
        
        # Значения условия
        self.values_layout = QHBoxLayout()
        layout.addLayout(self.values_layout)
        
        # Кнопка удаления условия
        delete_btn = QPushButton("×")
        delete_btn.setObjectName("controlButton")
        delete_btn.clicked.connect(self.deleteLater)
        layout.addWidget(delete_btn)
        
        # Инициализация виджетов условия
        self._setup_condition_widgets(field_type, condition_type)

    def to_dict(self):
        """Сериализация условия в словарь"""
        values = {}
        if self.condition_type == "Длина":
            values = {
                'min': self.values_layout.itemAt(1).widget().value(),
                'max': self.values_layout.itemAt(3).widget().value()
            }
        elif self.condition_type == "Маска":
            values = {
                'pattern': self.values_layout.itemAt(0).widget().text()
            }
        elif self.condition_type == "Диапазон":
            values = {
                'min': self.values_layout.itemAt(1).widget().value(),
                'max': self.values_layout.itemAt(3).widget().value()
            }
        elif self.condition_type == "Диапазон дат":
            values = {
                'min': self.values_layout.itemAt(1).widget().date().toString(Qt.ISODate),
                'max': self.values_layout.itemAt(3).widget().date().toString(Qt.ISODate)
            }
        elif self.condition_type == "Точность":
            values = {
                'precision': self.values_layout.itemAt(1).widget().value()
            }
        
        return {
            'type': self.condition_type,
            'field_type': self.field_type,
            'values': values
        }

    @classmethod
    def from_dict(cls, data, parent=None):
        """Создание виджета условия из словаря"""
        widget = cls(data['field_type'], data['type'], parent)
        
        if data['type'] == "Длина":
            widget.values_layout.itemAt(1).widget().setValue(data['values']['min'])
            widget.values_layout.itemAt(3).widget().setValue(data['values']['max'])
        elif data['type'] == "Маска":
            widget.values_layout.itemAt(0).widget().setText(data['values']['pattern'])
        elif data['type'] == "Диапазон":
            widget.values_layout.itemAt(1).widget().setValue(data['values']['min'])
            widget.values_layout.itemAt(3).widget().setValue(data['values']['max'])
        elif data['type'] == "Диапазон дат":
            widget.values_layout.itemAt(1).widget().setDate(QDate.fromString(data['values']['min'], Qt.ISODate))
            widget.values_layout.itemAt(3).widget().setDate(QDate.fromString(data['values']['max'], Qt.ISODate))
        elif data['type'] == "Точность":
            widget.values_layout.itemAt(1).widget().setValue(data['values']['precision'])
        
        return widget

    def _setup_condition_widgets(self, field_type, condition_type):
        if condition_type == "Длина":
            self.values_layout.addWidget(QLabel("Мин:"))
            min_spin = QSpinBox()
            min_spin.setRange(0, 1000)
            self.values_layout.addWidget(min_spin)
            
            self.values_layout.addWidget(QLabel("Макс:"))
            max_spin = QSpinBox()
            max_spin.setRange(0, 1000)
            self.values_layout.addWidget(max_spin)
            
        elif condition_type == "Маска":
            mask_edit = QLineEdit()
            mask_edit.setPlaceholderText("Пример: +7 (999) \\D\\D\\D-\\d\\d-\\d\\d")
            self.values_layout.addWidget(mask_edit)
            
            # Добавляем кнопку помощи
            help_btn = QPushButton("?")
            help_btn.setObjectName("helpButton")
            help_btn.clicked.connect(self._show_mask_help)
            self.values_layout.addWidget(help_btn)
            
        elif condition_type == "Диапазон":
            if field_type == "money":
                self.values_layout.addWidget(QLabel("От:"))
                min_spin = QDoubleSpinBox()
                min_spin.setRange(0, 999999999.99)
                min_spin.setDecimals(2)
                min_spin.setSuffix(" ₽")
                self.values_layout.addWidget(min_spin)
                
                self.values_layout.addWidget(QLabel("До:"))
                max_spin = QDoubleSpinBox()
                max_spin.setRange(0, 999999999.99)
                max_spin.setDecimals(2)
                max_spin.setSuffix(" ₽")
                self.values_layout.addWidget(max_spin)
            else:
                self.values_layout.addWidget(QLabel("От:"))
                min_spin = QSpinBox()
                min_spin.setRange(-999999999, 999999999)
                self.values_layout.addWidget(min_spin)
                
                self.values_layout.addWidget(QLabel("До:"))
                max_spin = QSpinBox()
                max_spin.setRange(-999999999, 999999999)
                self.values_layout.addWidget(max_spin)
                
        elif condition_type == "Диапазон дат":
            self.values_layout.addWidget(QLabel("От:"))
            min_date = QDateEdit()
            min_date.setCalendarPopup(True)
            min_date.setDate(QDate.currentDate())
            self.values_layout.addWidget(min_date)
            
            self.values_layout.addWidget(QLabel("До:"))
            max_date = QDateEdit()
            max_date.setCalendarPopup(True)
            max_date.setDate(QDate.currentDate())
            self.values_layout.addWidget(max_date)
            
        elif condition_type == "Точность":
            self.values_layout.addWidget(QLabel("Знаков после запятой:"))
            precision = QSpinBox()
            precision.setRange(0, 10)
            self.values_layout.addWidget(precision)
        
        elif condition_type in ["Минимум", "Максимум"]:
            value = QDoubleSpinBox()
            value.setRange(-1000000, 1000000)
            value.setPrefix("₽ ")  # Добавляем символ валюты
            value.setDecimals(2)   # Два знака после запятой для денег
            self.values_layout.addWidget(value)

    def _show_mask_help(self):
        help_text = """
<h3>Формат маски ввода</h3>
<p>Используйте следующие символы для создания маски:</p>
<ul>
    <li><b>\\d</b> - любая цифра (0-9)</li>
    <li><b>\\D</b> - любая буква (A-Z, a-z)</li>
    <li><b>\\w</b> - любая буква или цифра</li>
    <li><b>\\s</b> - пробел</li>
    <li><b>[]</b> - набор допустимых символов. Например: [ABC] - только A, B или C</li>
</ul>
<p><b>Примеры масок:</b></p>
<ul>
    <li>Телефон: <code>+7 (\\d\\d\\d) \\d\\d\\d-\\d\\d-\\d\\d</code></li>
    <li>Артикул: <code>\\D\\D-\\d\\d\\d\\d</code></li>
    <li>Серия паспорта: <code>\\d\\d \\d\\d \\d\\d\\d\\d\\d\\d</code></li>
</ul>
"""
        msg = QMessageBox()
        msg.setWindowTitle("Справка по маске ввода")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

class FieldWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def to_dict(self):
        """Сериализация поля в словарь"""
        conditions = []
        for i in range(self.conditions_layout.count()):
            widget = self.conditions_layout.itemAt(i).widget()
            if isinstance(widget, ConditionWidget):
                conditions.append(widget.to_dict())
        
        return {
            'name': self.field_name.text(),
            'type': self.field_type.currentText(),
            'conditions': conditions
        }

    @classmethod
    def from_dict(cls, data, parent=None):
        """Создание виджета поля из словаря"""
        widget = cls(parent)
        widget.field_name.setText(data['name'])
        widget.field_type.setCurrentText(data['type'])
        
        for condition_data in data['conditions']:
            condition = ConditionWidget.from_dict(condition_data, widget)
            widget.conditions_layout.addWidget(condition)
        
        return widget

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # Кнопка удаления поля
        delete_field_btn = QPushButton("×")
        delete_field_btn.setObjectName("controlButton")
        delete_field_btn.clicked.connect(self.deleteLater)
        main_layout.addWidget(delete_field_btn)
        
        # Поле для имени
        self.field_name = QLineEdit()
        self.field_name.setPlaceholderText("Название поля")
        self.field_name.setFixedWidth(200)
        main_layout.addWidget(self.field_name)
        
        # Выбор типа поля
        self.field_type = QComboBox()
        self.field_type.addItems(["text", "number", "money", "date", "float"])
        self.field_type.setFixedWidth(100)
        main_layout.addWidget(self.field_type)
        
        # Контейнер для условий (теперь горизонтальный)
        self.conditions_layout = QHBoxLayout()
        self.conditions_layout.setSpacing(10)
        main_layout.addLayout(self.conditions_layout)
        
        # Кнопка добавления условия
        add_condition_btn = QPushButton("+")
        add_condition_btn.setObjectName("controlButton")
        add_condition_btn.clicked.connect(self.show_condition_selector)
        main_layout.addWidget(add_condition_btn)
        
        main_layout.addStretch()

    def get_available_conditions(self):
        field_type = self.field_type.currentText()
        conditions = {
            "text": ["Длина", "Маска"],
            "number": ["Диапазон", "Кратность"],
            "money": ["Диапазон"],
            "date": ["Диапазон дат"],
            "float": ["Диапазон", "Точность"]
        }
        return conditions.get(field_type, [])

    def show_condition_selector(self):
        conditions = self.get_available_conditions()
        if not conditions:
            return
            
        # Создаем меню с доступными условиями
        menu = QMenu(self)
        for condition in conditions:
            action = menu.addAction(condition)
            action.triggered.connect(lambda checked, c=condition: self.create_condition(c))
            
        # Показываем меню рядом с кнопкой
        button = self.sender()
        menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))

    def create_condition(self, condition_type):
        field_type = self.field_type.currentText()
        condition = ConditionWidget(field_type, condition_type)
        self.conditions_layout.addWidget(condition)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Редактор форматов товаров')
        self.setMinimumSize(1000, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # Добавляем панель инструментов
        toolbar = QHBoxLayout()
        main_layout.addLayout(toolbar)

        # Кнопка сохранения
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_to_file)
        save_btn.setFixedWidth(100)
        toolbar.addWidget(save_btn)

        # Кнопка загрузки
        load_btn = QPushButton("Загрузить")
        load_btn.clicked.connect(self.load_from_file)
        load_btn.setFixedWidth(100)
        toolbar.addWidget(load_btn)

        # Кнопка проверки XML
        validate_btn = QPushButton("Проверить XML")
        validate_btn.clicked.connect(self.validate_xml)
        validate_btn.setFixedWidth(100)
        toolbar.addWidget(validate_btn)

        toolbar.addStretch()
        
        # Создаем разделитель для основной области и отчета
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Верхняя часть с полями
        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_widget.setLayout(top_layout)
        
        # Создаем область прокрутки для полей
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        top_layout.addWidget(scroll_area)
        
        # Контейнер для полей
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout()
        self.fields_layout.setAlignment(Qt.AlignTop)
        self.fields_layout.setSpacing(10)
        self.fields_container.setLayout(self.fields_layout)
        
        # Кнопка добавления нового поля
        add_field_btn = QPushButton("Добавить поле")
        add_field_btn.setFixedWidth(200)
        add_field_btn.clicked.connect(self.add_field)
        self.fields_layout.addWidget(add_field_btn, alignment=Qt.AlignLeft)
        
        scroll_area.setWidget(self.fields_container)
        
        splitter.addWidget(top_widget)
        
        # Нижняя часть с отчетом
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMinimumHeight(200)
        splitter.addWidget(self.report_text)
        
        # Устанавливаем соотношение размеров частей сплиттера
        splitter.setSizes([600, 200])
        
        # Применяем стили
        self.apply_styles()

    def add_field(self):
        # Удаляем кнопку добавления
        add_button = self.fields_layout.itemAt(self.fields_layout.count() - 1).widget()
        self.fields_layout.removeWidget(add_button)
        
        # Создаем новое поле
        field = FieldWidget()
        self.fields_layout.addWidget(field)
        
        # Возвращаем кнопку в конец
        self.fields_layout.addWidget(add_button, alignment=Qt.AlignLeft)
        
        return field

    def apply_styles(self):
        # Устанавливаем теплую цветовую схему
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 250, 240))  # Теплый светлый фон
        palette.setColor(QPalette.WindowText, QColor(70, 40, 20))  # Темно-коричневый текст
        palette.setColor(QPalette.Base, QColor(255, 252, 245))    # Светлый фон для полей ввода
        palette.setColor(QPalette.AlternateBase, QColor(255, 248, 235))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 252, 245))
        palette.setColor(QPalette.ToolTipText, QColor(70, 40, 20))
        palette.setColor(QPalette.Text, QColor(70, 40, 20))
        palette.setColor(QPalette.Button, QColor(255, 228, 196))  # Теплый цвет для кнопок
        palette.setColor(QPalette.ButtonText, QColor(70, 40, 20))
        palette.setColor(QPalette.BrightText, QColor(191, 91, 23))
        palette.setColor(QPalette.Link, QColor(191, 91, 23))      # Теплый оранжевый для ссылок
        palette.setColor(QPalette.Highlight, QColor(255, 228, 196))
        palette.setColor(QPalette.HighlightedText, QColor(70, 40, 20))
        
        QApplication.setPalette(palette)
        QApplication.setStyle("Fusion")
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
        
        # Применяем стили ко всем виджетам
        style_sheet = """
            QPushButton {
                border-radius: 15px;
                padding: 8px 15px;
                background-color: #FFE4C4;
                border: 1px solid #DEB887;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #DEB887;
            }
            QPushButton:pressed {
                background-color: #D2B48C;
            }
            QPushButton#controlButton {
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
                padding: 0px;
                font-size: 24px;
                font-weight: bold;
                margin: 0px 10px;
            }
            QPushButton#helpButton {
                border-radius: 15px;
                min-width: 30px;
                min-height: 30px;
                max-width: 30px;
                max-height: 30px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
                margin: 0px 5px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                border-radius: 8px;
                padding: 5px;
                background-color: #FFFAF0;
                border: 1px solid #DEB887;
                min-height: 25px;
            }
            QSpinBox, QDoubleSpinBox {
                padding-right: 15px;
                min-width: 80px;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                height: 12px;
                border: none;
                border-left: 1px solid #DEB887;
                border-bottom: 1px solid #DEB887;
                border-top-right-radius: 8px;
                background-color: #FFE4C4;
                margin: 0px;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                height: 12px;
                border: none;
                border-left: 1px solid #DEB887;
                border-bottom-right-radius: 8px;
                background-color: #FFE4C4;
                margin: 0px;
            }
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #DEB887;
            }
            QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
            QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {
                background-color: #D2B48C;
            }
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                image: url(data:image/svg+xml,<svg width='16' height='16' viewBox='0 0 16 16' xmlns='http://www.w3.org/2000/svg'><path d='M8 4L4 8H12L8 4Z' fill='%23462814'/></svg>);
                width: 12px;
                height: 12px;
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                image: url(data:image/svg+xml,<svg width='16' height='16' viewBox='0 0 16 16' xmlns='http://www.w3.org/2000/svg'><path d='M8 12L12 8H4L8 12Z' fill='%23462814'/></svg>);
                width: 12px;
                height: 12px;
            }
            QFrame {
                border-radius: 10px;
                background-color: #FFFAF0;
                border: 1px solid #DEB887;
                padding: 5px;
            }
            QFrame#conditionFrame {
                border: 1px solid #964B00;
                border-radius: 10px;
                background-color: transparent;
                padding: 2px;
            }
            QScrollArea {
                border-radius: 10px;
                background-color: #FFFAF0;
                border: 1px solid #DEB887;
            }
            QDateEdit::drop-down {
                border: none;
                border-left: 1px solid #DEB887;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: #FFE4C4;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: url(data:image/svg+xml,<svg width='16' height='16' viewBox='0 0 16 16' xmlns='http://www.w3.org/2000/svg'><path d='M8 12L12 8H4L8 12Z' fill='%23462814'/></svg>);
                width: 12px;
                height: 12px;
            }
        """
        self.setStyleSheet(style_sheet)

    def save_to_file(self):
        """Сохранение данных в JSON файл"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конфигурацию",
            "",
            "JSON файлы (*.json);;Все файлы (*.*)"
        )
        
        if filename:
            data = []
            # Пропускаем последний элемент (кнопку добавления)
            for i in range(self.fields_layout.count() - 1):
                widget = self.fields_layout.itemAt(i).widget()
                if isinstance(widget, FieldWidget):
                    data.append(widget.to_dict())
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Успех", "Конфигурация успешно сохранена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def load_from_file(self):
        """Загрузка данных из JSON файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить конфигурацию",
            "",
            "JSON файлы (*.json);;Все файлы (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Очищаем текущие поля
                while self.fields_layout.count() > 1:  # Оставляем кнопку добавления
                    widget = self.fields_layout.itemAt(0).widget()
                    self.fields_layout.removeWidget(widget)
                    widget.deleteLater()
                
                # Загружаем поля из файла
                for field_data in data:
                    field = FieldWidget.from_dict(field_data, self.fields_container)
                    # Вставляем поле перед кнопкой добавления
                    self.fields_layout.insertWidget(self.fields_layout.count() - 1, field)
                
                QMessageBox.information(self, "Успех", "Конфигурация успешно загружена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def validate_xml(self):
        """Проверка XML файла на соответствие условиям"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите XML файл",
            "",
            "XML файлы (*.xml);;Все файлы (*.*)"
        )
        
        if not filename:
            return
            
        try:
            # Парсим XML файл
            tree = ET.parse(filename)
            root = tree.getroot()
            
            # Ищем тег offers
            offers_tag = root.find('.//offers')
            if offers_tag is None:
                raise ValueError("Тег <offers> не найден в файле")
            
            # Собираем все поля и их условия
            fields_conditions = {}
            for i in range(self.fields_layout.count() - 1):  # Исключаем кнопку добавления
                field_widget = self.fields_layout.itemAt(i).widget()
                if isinstance(field_widget, FieldWidget):
                    field_name = field_widget.field_name.text()
                    field_type = field_widget.field_type.currentText()
                    conditions = []
                    
                    for j in range(field_widget.conditions_layout.count()):
                        condition_widget = field_widget.conditions_layout.itemAt(j).widget()
                        if isinstance(condition_widget, ConditionWidget):
                            conditions.append({
                                'type': condition_widget.condition_type,
                                'field_type': field_type,
                                'values': condition_widget.to_dict()['values']
                            })
                    
                    fields_conditions[field_name] = {
                        'type': field_type,
                        'conditions': conditions
                    }
            
            # Проверяем каждый offer
            report = []
            total_offers = 0
            offers_with_errors = 0
            
            for offer in offers_tag.findall('offer'):
                total_offers += 1
                offer_id = offer.get('id', 'Неизвестный ID')
                offer_errors = []
                
                # Проверяем каждое поле
                for field_name, field_info in fields_conditions.items():
                    # Ищем значение поля
                    field_value = None
                    
                    # Сначала ищем как обычный тег
                    field_elem = offer.find(field_name)
                    if field_elem is not None:
                        field_value = field_elem.text
                    else:
                        # Если не нашли, ищем в param с атрибутом name
                        for param in offer.findall('param'):
                            if param.get('name') == field_name:
                                field_value = param.text
                                break
                    
                    if field_value is None:
                        offer_errors.append(f"  - Поле '{field_name}' не найдено")
                        continue
                    
                    # Проверяем каждое условие для поля
                    for condition in field_info['conditions']:
                        error = self.check_condition(field_value, condition, field_info['type'])
                        if error:
                            offer_errors.append(f"  - Поле '{field_name}': {error}")
                
                # Добавляем в отчет только если есть ошибки
                if offer_errors:
                    offers_with_errors += 1
                    report.append(f"\nТовар (ID: {offer_id}):")
                    report.extend(offer_errors)
            
            # Добавляем статистику в начало отчета
            stats = [
                "Результаты проверки:",
                f"Всего проверено товаров: {total_offers}",
                f"Товаров с ошибками: {offers_with_errors}",
                f"Товаров без ошибок: {total_offers - offers_with_errors}",
                "\nПодробный отчет об ошибках:"
            ]
            
            # Если нет ошибок, добавляем сообщение об этом
            if not report:
                stats.append("\nВсе товары соответствуют заданным условиям!")
            
            # Выводим отчет
            self.report_text.setText('\n'.join(stats + report))
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке файла: {str(e)}")

    def check_condition(self, value, condition, field_type):
        """Проверка значения на соответствие условию"""
        try:
            if condition['type'] == "Длина":
                if len(value) < condition['values']['min']:
                    return f"длина меньше минимальной ({len(value)} < {condition['values']['min']})"
                if len(value) > condition['values']['max']:
                    return f"длина больше максимальной ({len(value)} > {condition['values']['max']})"
                
            elif condition['type'] == "Маска":
                import re
                pattern = condition['values']['pattern']
                if not re.match(pattern, value):
                    return f"не соответствует маске '{pattern}'"
                
            elif condition['type'] == "Диапазон":
                if field_type in ["number", "money"]:
                    num_value = float(value.replace(',', '.'))
                    if num_value < condition['values']['min']:
                        return f"значение меньше минимального ({num_value} < {condition['values']['min']})"
                    if num_value > condition['values']['max']:
                        return f"значение больше максимального ({num_value} > {condition['values']['max']})"
                        
            elif condition['type'] == "Диапазон дат":
                date_value = datetime.strptime(value, "%Y-%m-%d").date()
                min_date = datetime.strptime(condition['values']['min'], "%Y-%m-%d").date()
                max_date = datetime.strptime(condition['values']['max'], "%Y-%m-%d").date()
                
                if date_value < min_date:
                    return f"дата раньше минимальной ({date_value} < {min_date})"
                if date_value > max_date:
                    return f"дата позже максимальной ({date_value} > {max_date})"
                    
            elif condition['type'] == "Точность":
                if field_type == "float":
                    decimal_places = len(value.split('.')[-1]) if '.' in value else 0
                    if decimal_places > condition['values']['precision']:
                        return f"слишком много знаков после запятой ({decimal_places} > {condition['values']['precision']})"
                        
        except (ValueError, TypeError) as e:
            return f"некорректное значение для проверки: {str(e)}"
            
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
