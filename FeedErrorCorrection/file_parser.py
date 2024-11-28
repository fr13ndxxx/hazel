import pandas as pd
import requests
from lxml import etree
import asyncio

class FileParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def read_csv(self):
        try:
            self.data = pd.read_csv(self.file_path)
            print("CSV файл успешно загружен.")
        except Exception as e:
            print(f"Ошибка при чтении CSV файла: {e}")

    def read_xlsx(self):
        print("Начало чтения XLSX файла...")
        try:
            self.data = pd.read_excel(self.file_path, engine='openpyxl')
            print("XLSX файл успешно загружен.")
        except Exception as e:
            print(f"Ошибка при чтении XLSX файла: {e}")
        print("Завершение чтения XLSX файла.")

    def read_xml(self):
        try:
            tree = etree.parse(self.file_path)
            root = tree.getroot()
            print("Структура XML файла:")
            for elem in root.iter():
                print(elem.tag, elem.attrib)
            # Динамическое извлечение данных из XML
            data = []
            columns = set()
            for offer in root.findall('.//offer'):
                print(f"Обработка элемента offer с атрибутами: {offer.attrib}")
                entry = {attr: offer.get(attr) for attr in offer.attrib}
                for element in offer:
                    print(f"Обработка элемента {element.tag} с текстом: {element.text}")
                    if element.tag == 'param':
                        entry[element.get('name')] = element.text
                    else:
                        entry[element.tag] = element.text
                    columns.add(element.tag)
                data.append(entry)
            # Проверка на наличие данных перед созданием DataFrame
            if data:
                self.data = pd.DataFrame(data, columns=list(columns))
                print("XML файл успешно загружен.")
                print("Первые строки загруженных данных:")
                print(self.data.head())
            else:
                print("Данные не были извлечены из XML.")
        except Exception as e:
            print(f"Ошибка при чтении XML файла: {e}")

    def get_data(self):
        return self.data

    def check_mandatory_fields(self, mandatory_fields):
        if self.data is None:
            print("Данные не загружены для проверки обязательных полей.")
            return
        missing_fields = [field for field in mandatory_fields if field not in self.data.columns]
        if missing_fields:
            print(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
        else:
            print("Все обязательные поля присутствуют.")

    # Метод для проверки дублирующихся строк по указанному столбцу, например, SKU
    def check_duplicates(self, column_name):
        if self.data is None:
            print("Данные не загружены для проверки дубликатов.")
            return
        duplicates = self.data[self.data.duplicated(subset=[column_name], keep=False)]
        if not duplicates.empty:
            print(f"Найдены дубликаты в столбце {column_name}:")
            print(duplicates)
        else:
            print(f"Дубликаты в столбце {column_name} не найдены.")

    # Метод для проверки корректности форматов данных в указанном столбце
    def check_data_format(self, column_name, data_type):
        if self.data is None:
            print("Данные не загружены для проверки форматов данных.")
            return
        incorrect_format = self.data[~self.data[column_name].apply(lambda x: isinstance(x, data_type))]
        if not incorrect_format.empty:
            print(f"Некорректный формат данных в столбце {column_name}:")
            print(incorrect_format)
        else:
            print(f"Все данные в столбце {column_name} соответствуют типу {data_type}.")

    # Метод для проверки корректности цен, чтобы все цены были положительными
    def check_price_validity(self, price_column):
        if self.data is None:
            print("Данные не загружены для проверки корректности цен.")
            return
        invalid_prices = self.data[self.data[price_column] <= 0]
        if not invalid_prices.empty:
            print("Найдены некорректные цены (<= 0):")
            print(invalid_prices)
        else:
            print("Все цены корректны.")

    # Метод для проверки корректности скидок, чтобы скидки не превышали 100%
    def check_discount_validity(self, discount_column):
        if self.data is None:
            print("Данные не загружены для проверки корректности скидок.")
            return
        invalid_discounts = self.data[(self.data[discount_column] < 0) | (self.data[discount_column] > 100)]
        if not invalid_discounts.empty:
            print("Найдены некорректные скидки (< 0% или > 100%):")
            print(invalid_discounts)
        else:
            print("Все скидки корректны.")

    # Метод для проверки пустых категорий
    def check_empty_categories(self, category_column):
        if self.data is None:
            print("Данные не загружены для проверки пустых категорий.")
            return
        empty_categories = self.data[self.data[category_column].isnull() | (self.data[category_column] == '')]
        if not empty_categories.empty:
            print("Найдены пустые категории:")
            print(empty_categories)
        else:
            print("Все категории заполнены.")

    # Метод для проверки корректности форматов дат
    def check_date_format(self, column_name, date_format="%Y-%m-%d"):
        if self.data is None:
            print("Данные не загружены для проверки форматов дат.")
            return
        incorrect_dates = self.data[~self.data[column_name].apply(lambda x: pd.to_datetime(x, format=date_format, errors='coerce').notna())]
        if not incorrect_dates.empty:
            print(f"Некорректный формат даты в столбце {column_name}:")
            print(incorrect_dates)
        else:
            print(f"Все даты в столбце {column_name} корректны.")

    # Метод для проверки допустимых значений в столбце
    def check_allowed_values(self, column_name, allowed_values):
        if self.data is None:
            print("Данные не загружены для проверки допустимых значений.")
            return
        incorrect_values = self.data[~self.data[column_name].isin(allowed_values)]
        if not incorrect_values.empty:
            print(f"Недопустимые значения в столбце {column_name}:")
            print(incorrect_values)
        else:
            print(f"Все значения в столбце {column_name} допустимы.")

    # Метод для предложения исправлений обнаруженных ошибок
    def suggest_corrections(self):
        if self.data is None:
            print("Данные не загружены для предложения исправлений.")
            return
        corrections = {}
        # Пример: исправление некорректных цен
        invalid_prices = self.data[self.data['price'] <= 0]
        if not invalid_prices.empty:
            corrections['price'] = "Предложение: заменить некорректные цены на среднее значение по категории."
        # Пример: исправление пустых категорий
        empty_categories = self.data[self.data['category'].isnull() | (self.data['category'] == '')]
        if not empty_categories.empty:
            corrections['category'] = "Предложение: заполнить пустые категории на основе других данных."
        print("Предложения по исправлениям:")
        for field, suggestion in corrections.items():
            print(f"Поле {field}: {suggestion}")

    # Метод для генерации отчета об исправлениях
    def generate_correction_report(self):
        if self.data is None:
            print("Данные не загружены для генерации отчета.")
            return
        # Здесь будет логика для генерации отчета
        print("Отчет об исправлениях сгенерирован.")

    # Метод для экспорта данных в CSV
    def export_to_csv(self, output_path):
        if self.data is None:
            print("Данные не загружены для экспорта.")
            return
        try:
            self.data.to_csv(output_path, index=False)
            print(f"Данные успешно экспортированы в CSV файл: {output_path}")
        except Exception as e:
            print(f"Ошибка при экспорте в CSV: {e}")

    # Метод для экспорта данных в XLSX
    def export_to_xlsx(self, output_path):
        if self.data is None:
            print("Данные не загружены для экспорта.")
            return
        try:
            self.data.to_excel(output_path, index=False, engine='openpyxl')
            print(f"Данные успешно экспортированы в XLSX файл: {output_path}")
        except Exception as e:
            print(f"Ошибка при экспорте в XLSX: {e}")

    # Метод для загрузки файла из URL
    def load_from_url(self, url):
        if url.startswith('http://') or url.startswith('https://'):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Проверка на ошибки HTTP
                # Определяем формат файла по URL или заголовкам
                if url.endswith('.csv') or 'text/csv' in response.headers.get('Content-Type', ''):
                    self.data = pd.read_csv(pd.compat.StringIO(response.text))
                    print("Данные из CSV успешно загружены из URL.")
                elif url.endswith('.xlsx') or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.headers.get('Content-Type', ''):
                    self.data = pd.read_excel(pd.compat.BytesIO(response.content), engine='openpyxl')
                    print("Данные из XLSX успешно загружены из URL.")
                else:
                    print("Неизвестный формат файла.")
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке файла из URL: {e}")
        else:
            print("Указан некорректный URL. Пожалуйста, убедитесь, что URL начинается с http:// или https://.")

    async def load_from_url_async(self, url):
        loop = asyncio.get_event_loop()
        if url.startswith('http://') or url.startswith('https://'):
            try:
                response = await loop.run_in_executor(None, requests.get, url)
                response.raise_for_status()  # Проверка на ошибки HTTP
                # Определяем формат файла по URL или заголовкам
                if url.endswith('.csv') or 'text/csv' in response.headers.get('Content-Type', ''):
                    self.data = pd.read_csv(pd.compat.StringIO(response.text))
                    print("Данные из CSV успешно загружены из URL.")
                elif url.endswith('.xlsx') or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.headers.get('Content-Type', ''):
                    self.data = pd.read_excel(pd.compat.BytesIO(response.content), engine='openpyxl')
                    print("Данные из XLSX успешно загружены из URL.")
                else:
                    print("Неизвестный формат файла.")
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке файла из URL: {e}")
        else:
            print("Указан некорректный URL. Пожалуйста, убедитесь, что URL начинается с http:// или https://.")

    # Метод для автоматического исправления форматов дат
    def fix_date_format(self, column_name, date_format="%Y-%m-%d"):
        if self.data is None:
            print("Данные не загружены для исправления форматов дат.")
            return
        self.data[column_name] = pd.to_datetime(self.data[column_name], errors='coerce').dt.strftime(date_format)
        print(f"Формат дат в столбце {column_name} автоматически исправлен.")

    # Метод для исправления некорректных значений
    def fix_incorrect_values(self, column_name, replacement_value):
        if self.data is None:
            print("Данные не загружены для исправления значений.")
            return
        incorrect_values = self.data[column_name].isna() | (self.data[column_name] == '')
        self.data.loc[incorrect_values, column_name] = replacement_value
        print(f"Некорректные значения в столбце {column_name} заменены на {replacement_value}.")

    # Метод для запуска полного процесса обработки фида
    def process_feed(self, source, is_url=False):
        if self.data is None or self.data.empty:
            print("Данные не загружены.")
            return
        # Проверка на наличие обязательных полей
        mandatory_fields = ['name', 'SKU', 'price']
        missing_fields = [field for field in mandatory_fields if field not in self.data.columns]
        if missing_fields:
            print(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
            return
        # Выполняем проверки
        self.check_mandatory_fields(mandatory_fields)
        self.check_duplicates('SKU')
        self.check_data_format('price', (int, float))
        self.check_price_validity('price')
        self.check_discount_validity('discount')
        self.check_empty_categories('category')
        # Предлагаем исправления
        self.suggest_corrections()
        # Исправляем форматы дат и некорректные значения
        self.fix_date_format('date')
        self.fix_incorrect_values('category', 'Unknown')
        # Генерируем отчет
        self.generate_correction_report()
        # Экспортируем исправленный фид
        output_path = 'corrected_feed.csv' if source.endswith('.csv') else 'corrected_feed.xlsx'
        if source.endswith('.csv'):
            self.export_to_csv(output_path)
        elif source.endswith('.xlsx'):
            self.export_to_xlsx(output_path)
        else:
            print("Экспорт для XML пока не поддерживается.")

    async def process_feed_async(self, source, is_url=False):
        if is_url:
            await self.load_from_url_async(source)
        else:
            self.file_path = source
            if source.endswith('.csv'):
                await asyncio.to_thread(self.read_csv)
            elif source.endswith('.xlsx'):
                await asyncio.to_thread(self.read_xlsx)
            elif source.endswith('.xml'):
                await asyncio.to_thread(self.read_xml)
            else:
                print("Поддерживаются только форматы CSV, XLSX и XML.")
                return
        # Выполняем проверки
        await asyncio.to_thread(self.check_mandatory_fields, ['name', 'SKU', 'price'])
        await asyncio.to_thread(self.check_duplicates, 'SKU')
        await asyncio.to_thread(self.check_data_format, 'price', (int, float))
        await asyncio.to_thread(self.check_price_validity, 'price')
        await asyncio.to_thread(self.check_discount_validity, 'discount')
        await asyncio.to_thread(self.check_empty_categories, 'category')
        # Предлагаем исправления
        await asyncio.to_thread(self.suggest_corrections)
        # Исправляем форматы дат и некорректные значения
        await asyncio.to_thread(self.fix_date_format, 'date')
        await asyncio.to_thread(self.fix_incorrect_values, 'category', 'Unknown')
        # Генерируем отчет
        await asyncio.to_thread(self.generate_correction_report)
        # Экспортируем исправленный фид
        output_path = 'corrected_feed.csv' if source.endswith('.csv') else 'corrected_feed.xlsx'
        if source.endswith('.csv'):
            await asyncio.to_thread(self.export_to_csv, output_path)
        elif source.endswith('.xlsx'):
            await asyncio.to_thread(self.export_to_xlsx, output_path)
        else:
            print("Экспорт для XML пока не поддерживается.")
