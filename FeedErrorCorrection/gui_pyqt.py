from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QMainWindow, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
import sys
from file_parser import FileParser

class FeedCorrectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feed Error Correction System")
        self.setGeometry(100, 100, 600, 500)
        self.file_parser = None
        self.initUI()

    def initUI(self):
        # Установка шрифта для всех виджетов
        font = QFont()
        font.setPointSize(14)

        # Основной макет
        main_layout = QVBoxLayout()

        # Кнопка для загрузки файла
        self.load_button = QtWidgets.QPushButton("Загрузить файл")
        self.load_button.setFont(font)
        self.load_button.clicked.connect(self.load_file)
        main_layout.addWidget(self.load_button)

        # Поле для ввода URL и кнопка загрузки из URL
        url_layout = QHBoxLayout()
        self.url_entry = QtWidgets.QLineEdit()
        self.url_entry.setPlaceholderText("Введите URL для загрузки файла")
        self.url_entry.setFont(font)
        url_layout.addWidget(self.url_entry)

        self.load_url_button = QtWidgets.QPushButton("Загрузить из URL")
        self.load_url_button.setFont(font)
        self.load_url_button.clicked.connect(self.load_from_url)
        url_layout.addWidget(self.load_url_button)

        main_layout.addLayout(url_layout)

        # Выпадающий список для выбора формата экспорта
        self.export_format_combo = QtWidgets.QComboBox()
        self.export_format_combo.setFont(font)
        self.export_format_combo.addItems(["CSV", "XLSX"])
        main_layout.addWidget(self.export_format_combo)

        # Кнопка для обработки фида
        self.process_button = QtWidgets.QPushButton("Обработать фид")
        self.process_button.setFont(font)
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_feed)
        main_layout.addWidget(self.process_button)

        # Поле для отображения статуса
        self.status_text = QtWidgets.QTextEdit()
        self.status_text.setFont(font)
        self.status_text.setReadOnly(True)
        self.status_text.setText("Статус: Ожидание загрузки файла...")
        main_layout.addWidget(self.status_text)

        # Поле для ввода формата даты
        self.date_format_entry = QtWidgets.QLineEdit()
        self.date_format_entry.setPlaceholderText("Введите формат даты (например, %Y-%m-%d)")
        self.date_format_entry.setFont(font)
        main_layout.addWidget(self.date_format_entry)

        # Поле для ввода допустимых категорий
        self.allowed_categories_entry = QtWidgets.QLineEdit()
        self.allowed_categories_entry.setPlaceholderText("Введите допустимые категории через запятую")
        self.allowed_categories_entry.setFont(font)
        main_layout.addWidget(self.allowed_categories_entry)

        # Установка основного макета
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "CSV files (*.csv);;Excel files (*.xlsx);;XML files (*.xml);;All files (*)")
        if file_path:
            self.file_parser = FileParser(file_path)
            self.file_parser.process_feed(file_path, is_url=False)
            QMessageBox.information(self, "Файл загружен", f"Файл {file_path} успешно загружен и обработан.")
            self.process_button.setEnabled(True)

    def load_from_url(self):
        url = self.url_entry.text()
        if url:
            self.file_parser = FileParser(url)
            self.file_parser.load_from_url(url)
            if self.file_parser.data is not None:
                QMessageBox.information(self, "Файл загружен", "Файл из URL успешно загружен и обработан.")
                self.process_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить файл из URL.")

    def process_feed(self):
        if self.file_parser:
            self.status_text.append("Начало обработки фида...")
            # Получаем параметры от пользователя
            date_format = self.date_format_entry.text() or "%Y-%m-%d"
            allowed_categories = self.allowed_categories_entry.text().split(',') if self.allowed_categories_entry.text() else []
            # Обновляем процесс обработки с учетом параметров
            self.file_parser.fix_date_format('date', date_format)
            if allowed_categories:
                self.file_parser.check_allowed_values('category', allowed_categories)
            self.status_text.append("Фид успешно обработан.")
            export_format = self.export_format_combo.currentText()
            if export_format == "CSV":
                self.file_parser.export_to_csv("corrected_feed.csv")
                self.status_text.append("Фид экспортирован в CSV.")
            else:
                self.file_parser.export_to_xlsx("corrected_feed.xlsx")
                self.status_text.append("Фид экспортирован в XLSX.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FeedCorrectionApp()
    window.show()
    sys.exit(app.exec_())
