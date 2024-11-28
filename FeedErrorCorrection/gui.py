import tkinter as tk
from tkinter import filedialog, messagebox
from file_parser import FileParser

class FeedCorrectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Feed Error Correction System")
        self.file_parser = None

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Кнопка для загрузки файла
        self.load_button = tk.Button(self.root, text="Загрузить файл", command=self.load_file)
        self.load_button.pack(pady=10)

        # Поле для ввода URL
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=10)
        self.url_entry.insert(0, "Введите URL для загрузки файла")

        # Кнопка для загрузки из URL
        self.load_url_button = tk.Button(self.root, text="Загрузить из URL", command=self.load_from_url)
        self.load_url_button.pack(pady=10)

        # Выпадающий список для выбора формата экспорта
        self.export_format_var = tk.StringVar(value="CSV")
        self.export_format_menu = tk.OptionMenu(self.root, self.export_format_var, "CSV", "XLSX")
        self.export_format_menu.pack(pady=10)

        # Кнопка для обработки фида
        self.process_button = tk.Button(self.root, text="Обработать фид", command=self.process_feed, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        # Поле для отображения статуса
        self.status_text = tk.Text(self.root, height=10, width=60)
        self.status_text.pack(pady=10)
        self.status_text.insert(tk.END, "Статус: Ожидание загрузки файла...")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if file_path:
            self.file_parser = FileParser(file_path)
            messagebox.showinfo("Файл загружен", f"Файл {file_path} успешно загружен.")
            self.process_button.config(state=tk.NORMAL)

    def load_from_url(self):
        url = self.url_entry.get()
        if url:
            self.file_parser = FileParser(url)
            self.file_parser.load_from_url(url)
            self.status_text.insert(tk.END, "\nФайл из URL успешно загружен.")
            self.process_button.config(state=tk.NORMAL)

    def process_feed(self):
        if self.file_parser:
            self.status_text.insert(tk.END, "\nНачало обработки фида...")
            self.file_parser.process_feed(self.file_parser.file_path, is_url=True)
            self.status_text.insert(tk.END, "\nФид успешно обработан.")
            # Экспортируем в выбранном формате
            export_format = self.export_format_var.get()
            if export_format == "CSV":
                self.file_parser.export_to_csv("corrected_feed.csv")
                self.status_text.insert(tk.END, "\nФид экспортирован в CSV.")
            else:
                self.file_parser.export_to_xlsx("corrected_feed.xlsx")
                self.status_text.insert(tk.END, "\nФид экспортирован в XLSX.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FeedCorrectionApp(root)
    root.mainloop()
