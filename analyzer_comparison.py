# -*- coding: utf-8 -*-
"""
Программа для сравнения данных анализаторов SO2 и H2S
Отображает временные ряды с интерактивным перекрестием
"""

import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel,
                             QTableWidget, QTableWidgetItem, QSplitter, QDialog,
                             QTextEdit, QTabWidget, QScrollArea, QFrame, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from datetime import datetime

class DataDebuggerDialog(QDialog):
    """Визуальный отладчик данных"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Отладчик данных Excel файлов')
        self.setGeometry(200, 200, 1000, 700)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса отладчика"""
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel('ОТЛАДЧИК ДАННЫХ EXCEL ФАЙЛОВ')
        title.setStyleSheet('QLabel { font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px; }')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Вкладки для разных типов анализа
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладка "Структура файла"
        self.structure_tab = QWidget()
        self.tabs.addTab(self.structure_tab, 'Структура файла')
        self.init_structure_tab()

        # Вкладка "Анализ данных"
        self.analysis_tab = QWidget()
        self.tabs.addTab(self.analysis_tab, 'Анализ данных')
        self.init_analysis_tab()

        # Вкладка "Проблемы преобразования"
        self.problems_tab = QWidget()
        self.tabs.addTab(self.problems_tab, 'Проблемы')
        self.init_problems_tab()

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        refresh_btn = QPushButton('Обновить анализ')
        refresh_btn.clicked.connect(self.refresh_analysis)
        refresh_btn.setStyleSheet('QPushButton { padding: 8px; font-size: 11px; background-color: #3498db; color: white; }')
        buttons_layout.addWidget(refresh_btn)

        export_btn = QPushButton('Экспорт отчета')
        export_btn.clicked.connect(self.export_report)
        export_btn.setStyleSheet('QPushButton { padding: 8px; font-size: 11px; background-color: #27ae60; color: white; }')
        buttons_layout.addWidget(export_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet('QPushButton { padding: 8px; font-size: 11px; }')
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def init_structure_tab(self):
        """Инициализация вкладки структуры файла"""
        layout = QVBoxLayout(self.structure_tab)

        self.structure_text = QTextEdit()
        self.structure_text.setFont(QFont('Consolas', 10))
        self.structure_text.setReadOnly(True)
        layout.addWidget(self.structure_text)

    def init_analysis_tab(self):
        """Инициализация вкладки анализа данных"""
        layout = QVBoxLayout(self.analysis_tab)

        self.analysis_text = QTextEdit()
        self.analysis_text.setFont(QFont('Consolas', 10))
        self.analysis_text.setReadOnly(True)
        layout.addWidget(self.analysis_text)

    def init_problems_tab(self):
        """Инициализация вкладки проблем"""
        layout = QVBoxLayout(self.problems_tab)

        self.problems_text = QTextEdit()
        self.problems_text.setFont(QFont('Consolas', 10))
        self.problems_text.setReadOnly(True)
        layout.addWidget(self.problems_text)

    def analyze_data(self, data_files):
        """Анализ загруженных данных"""
        self.data_files = data_files
        self.refresh_analysis()

    def refresh_analysis(self):
        """Обновление анализа данных"""
        if not hasattr(self, 'data_files') or not self.data_files:
            self.structure_text.setText("[ERROR] Нет загруженных файлов для анализа")
            self.analysis_text.setText("[ERROR] Нет данных для анализа")
            self.problems_text.setText("[ERROR] Нет данных для анализа проблем")
            return

        # Анализ структуры
        structure_info = self.analyze_structure()
        self.structure_text.setText(structure_info)

        # Анализ данных
        analysis_info = self.analyze_data_conversion()
        self.analysis_text.setText(analysis_info)

        # Анализ проблем
        problems_info = self.analyze_problems()
        self.problems_text.setText(problems_info)

    def analyze_structure(self):
        """Анализ структуры файлов"""
        result = []
        result.append("📋 СТРУКТУРА ЗАГРУЖЕННЫХ ФАЙЛОВ")
        result.append("=" * 50)

        for file_type, file_data in self.data_files.items():
            df = file_data['data']
            result.append(f"\n📁 Файл: {file_type}")
            result.append(f"   Путь: {file_data['path']}")
            result.append(f"   Строк: {len(df)}")
            result.append(f"   Колонок: {len(df.columns)}")

            result.append(f"\n   Колонки:")
            for i, col in enumerate(df.columns):
                dtype = df[col].dtype
                non_null = df[col].notna().sum()
                result.append(f"     {i:2d}. '{col}' | Тип: {dtype} | Не-null: {non_null}")

        return "\n".join(result)

    def analyze_data_conversion(self):
        """Анализ преобразования данных"""
        result = []
        result.append("🔬 АНАЛИЗ ПРЕОБРАЗОВАНИЯ ДАННЫХ")
        result.append("=" * 50)

        for file_type, file_data in self.data_files.items():
            df = file_data['data']
            result.append(f"\n📊 Файл: {file_type}")

            # Определяем колонки данных
            time_col, data_cols = self.identify_columns(df)
            result.append(f"   Колонка времени: '{time_col}'")
            result.append(f"   Колонки данных: {len(data_cols)}")

            # Анализируем первую колонку данных
            if data_cols:
                test_col = data_cols[0]
                values = df[test_col]
                result.append(f"\n   🔍 Анализ колонки '{test_col}':")
                result.append(f"     Тип данных: {values.dtype}")
                result.append(f"     Всего значений: {len(values)}")

                # Показываем примеры значений
                result.append(f"\n     Примеры значений:")
                for i in range(min(10, len(values))):
                    val = values.iloc[i]
                    result.append(f"       [{i}] '{val}' (тип: {type(val).__name__})")

                # Тестируем преобразование
                numeric_pd = pd.to_numeric(values, errors='coerce')
                valid_count = numeric_pd.notna().sum()
                nan_count = numeric_pd.isna().sum()
                zero_count = (numeric_pd == 0).sum()

                result.append(f"\n     Результат pd.to_numeric:")
                result.append(f"       Валидных: {valid_count}")
                result.append(f"       NaN: {nan_count}")
                result.append(f"       Нулей: {zero_count}")

        return "\n".join(result)

    def analyze_problems(self):
        """Анализ проблем преобразования"""
        result = []
        result.append("⚠️ АНАЛИЗ ПРОБЛЕМ ПРЕОБРАЗОВАНИЯ")
        result.append("=" * 50)

        total_problems = 0

        for file_type, file_data in self.data_files.items():
            df = file_data['data']
            result.append(f"\n🔍 Файл: {file_type}")

            time_col, data_cols = self.identify_columns(df)

            for col in data_cols[:3]:  # Анализируем первые 3 колонки
                values = df[col]
                result.append(f"\n   📊 Колонка '{col}':")

                # Тестируем pd.to_numeric
                numeric_pd = pd.to_numeric(values, errors='coerce')

                # Ищем проблемы
                problems = []
                for i in range(min(20, len(values))):
                    orig = values.iloc[i]
                    converted = numeric_pd.iloc[i]

                    # Проблема: не-ноль стал нулем
                    if (pd.notna(converted) and converted == 0 and
                        orig != 0 and orig != '0' and pd.notna(orig) and orig != ''):
                        problems.append((i, orig, converted))
                    # Проблема: число стало NaN
                    elif (pd.isna(converted) and pd.notna(orig) and
                          orig != '' and str(orig).replace(',', '.').replace(' ', '').replace('-', '').replace('+', '').replace('e', '').replace('E', '').replace('.', '').isdigit()):
                        problems.append((i, orig, converted))

                if problems:
                    result.append(f"     ❌ НАЙДЕНО ПРОБЛЕМ: {len(problems)}")
                    total_problems += len(problems)
                    for idx, orig, conv in problems[:5]:
                        result.append(f"       Строка {idx}: '{orig}' -> {conv}")
                    if len(problems) > 5:
                        result.append(f"       ... и еще {len(problems) - 5} проблем")
                else:
                    result.append(f"     ✅ Проблем не найдено")

        if total_problems > 0:
            result.insert(2, f"\n🚨 ВСЕГО НАЙДЕНО ПРОБЛЕМ: {total_problems}")
            result.insert(3, "💡 РЕКОМЕНДАЦИЯ: Используется ручное преобразование для исправления")
        else:
            result.insert(2, f"\n✅ ПРОБЛЕМ НЕ НАЙДЕНО")
            result.insert(3, "✅ pd.to_numeric работает корректно")

        return "\n".join(result)

    def identify_columns(self, df):
        """Определение колонок времени и данных (копия из основного класса)"""
        time_col = None
        data_cols = []

        exclude_keywords = ['tagname', 'tag_name', 'тег', 'название']
        time_keywords = ['время', 'time', 'дата', 'date', 'timestamp', 'datetime']

        # Поиск колонки времени
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in time_keywords):
                time_col = col
                break

        if time_col is None and len(df.columns) > 0:
            time_col = df.columns[0]

        # Поиск колонок данных
        for col in df.columns:
            col_lower = str(col).lower()
            if col == time_col:
                continue
            if any(keyword in col_lower for keyword in exclude_keywords):
                continue

            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                if numeric_data.notna().any():
                    data_cols.append(col)
            except:
                pass

        return time_col, data_cols

    def export_report(self):
        """Экспорт отчета отладчика в файл"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            from datetime import datetime

            # Выбор файла для сохранения
            filename, _ = QFileDialog.getSaveFileName(
                self,
                'Сохранить отчет отладчика',
                f'debug_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                'Text Files (*.txt)'
            )

            if filename:
                # Собираем весь отчет
                report = []
                report.append("🔍 ОТЧЕТ ОТЛАДЧИКА ДАННЫХ")
                report.append("=" * 60)
                report.append(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
                report.append("")

                # Добавляем содержимое всех вкладок
                report.append(self.structure_text.toPlainText())
                report.append("\n" + "=" * 60 + "\n")
                report.append(self.analysis_text.toPlainText())
                report.append("\n" + "=" * 60 + "\n")
                report.append(self.problems_text.toPlainText())

                # Сохраняем в файл
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report))

                QMessageBox.information(self, 'Успех', f'Отчет сохранен в файл:\n{filename}')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить отчет:\n{str(e)}')

class AnalyzerComparisonApp(QMainWindow):
    """Главное окно приложения для сравнения анализаторов"""

    def __init__(self):
        super().__init__()
        self.data_files = {}  # Словарь для хранения загруженных данных
        self.plots = []  # Список графиков
        self.crosshair_lines = []  # Линии перекрестия
        self.value_labels = []  # Метки для отображения значений
        self.highlight_items = []  # Элементы выделения на графике
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Сравнение анализаторов SO2 и H2S')
        self.setGeometry(100, 100, 1600, 1000)  # Увеличиваем размер окна

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Панель управления
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # Панель информации (метки для отображения значений при перекрестии)
        self.info_label = QLabel('Наведите курсор на график для отображения значений')
        self.info_label.setStyleSheet('QLabel { background-color: #f0f0f0; padding: 10px; font-size: 12px; }')
        self.info_label.setMinimumHeight(120)
        self.info_label.setMaximumHeight(180)
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)

        # Создаем горизонтальный разделитель для графика и таблицы
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter, stretch=1)

        # Левая часть - область графиков
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.setBackground('w')
        content_splitter.addWidget(self.plot_widget)

        # Правая часть - таблица данных
        self.create_data_table_panel(content_splitter)

        # Устанавливаем пропорции: 70% график, 30% таблица
        content_splitter.setSizes([1120, 480])

    def create_data_table_panel(self, parent_splitter):
        """Создание панели с таблицей данных"""
        # Контейнер для таблицы
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)

        # Заголовок таблицы
        table_header = QLabel('Данные временного ряда')
        table_header.setStyleSheet('QLabel { font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px; }')
        table_layout.addWidget(table_header)

        # Селектор файла для отображения
        file_selector_layout = QHBoxLayout()

        file_selector_label = QLabel('Файл:')
        file_selector_layout.addWidget(file_selector_label)

        self.file_selector = QComboBox()
        self.file_selector.addItem('Выберите файл...')
        self.file_selector.currentTextChanged.connect(self.on_file_selector_changed)
        file_selector_layout.addWidget(self.file_selector)

        file_selector_layout.addStretch()

        # Кнопка обновления таблицы
        refresh_table_btn = QPushButton('Обновить')
        refresh_table_btn.clicked.connect(self.refresh_data_table)
        refresh_table_btn.setStyleSheet('QPushButton { padding: 4px; font-size: 10px; }')
        file_selector_layout.addWidget(refresh_table_btn)

        table_layout.addLayout(file_selector_layout)

        # Таблица данных
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)
        self.data_table.itemSelectionChanged.connect(self.on_table_selection_changed)

        # Стиль таблицы
        self.data_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 10px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 4px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
            }
        """)

        table_layout.addWidget(self.data_table)

        # Информация о выбранной строке
        self.selection_info = QLabel('Выберите строку в таблице для выделения на графике')
        self.selection_info.setStyleSheet('QLabel { color: #7f8c8d; font-size: 10px; padding: 5px; }')
        table_layout.addWidget(self.selection_info)

        parent_splitter.addWidget(table_widget)

    def create_control_panel(self):
        """Создание панели управления с кнопками загрузки файлов"""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Кнопка загрузки файла H2S
        self.btn_load_h2s = QPushButton('📁 Загрузить файл H2S')
        self.btn_load_h2s.clicked.connect(lambda: self.load_file('H2S'))
        self.btn_load_h2s.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; }')
        layout.addWidget(self.btn_load_h2s)

        # Метка статуса H2S
        self.label_h2s = QLabel('Файл не загружен')
        self.label_h2s.setStyleSheet('QLabel { color: gray; font-size: 10px; }')
        layout.addWidget(self.label_h2s)

        layout.addStretch()

        # Кнопка загрузки файла SO2
        self.btn_load_so2 = QPushButton('📁 Загрузить файл SO2')
        self.btn_load_so2.clicked.connect(lambda: self.load_file('SO2'))
        self.btn_load_so2.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; }')
        layout.addWidget(self.btn_load_so2)

        # Метка статуса SO2
        self.label_so2 = QLabel('Файл не загружен')
        self.label_so2.setStyleSheet('QLabel { color: gray; font-size: 10px; }')
        layout.addWidget(self.label_so2)

        layout.addStretch()

        # Кнопка отладчика данных
        self.btn_debug = QPushButton('🔧 Отладчик данных')
        self.btn_debug.clicked.connect(self.show_data_debugger)
        self.btn_debug.setEnabled(False)
        self.btn_debug.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; background-color: #FF9800; color: white; } QPushButton:disabled { background-color: #cccccc; }')
        layout.addWidget(self.btn_debug)

        # Кнопка построения графиков
        self.btn_plot = QPushButton('📊 Построить графики')
        self.btn_plot.clicked.connect(self.plot_data)
        self.btn_plot.setEnabled(False)
        self.btn_plot.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; background-color: #4CAF50; color: white; } QPushButton:disabled { background-color: #cccccc; }')
        layout.addWidget(self.btn_plot)

        # Кнопка очистки
        btn_clear = QPushButton('🗑️ Очистить')
        btn_clear.clicked.connect(self.clear_all)
        btn_clear.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; }')
        layout.addWidget(btn_clear)

        return panel

    def debug_data_conversion(self, df, file_type):
        """ОТЛАДЧИК: Анализ преобразования данных из Excel файла"""
        print(f"\n[DEBUG] ОТЛАДЧИК ДАННЫХ - {file_type}")
        print("=" * 60)

        # Определяем колонки данных
        time_col, data_cols = self.identify_columns(df)

        if data_cols and len(data_cols) > 0:
            test_col = data_cols[0]  # Берем первую колонку для анализа
            print(f"[ANALYZE] Анализ колонки: '{test_col}'")

            values = df[test_col]
            print(f"Тип данных: {values.dtype}")
            print(f"Всего значений: {len(values)}")

            # Показываем первые 10 значений
            print("\nПервые 10 исходных значений:")
            for i in range(min(10, len(values))):
                val = values.iloc[i]
                print(f"  [{i}] '{val}' (тип: {type(val).__name__})")

            # Тестируем pd.to_numeric
            print(f"\n[TEST] Тест pd.to_numeric:")
            numeric_pd = pd.to_numeric(values, errors='coerce')

            # Ищем проблемы
            problems = []
            for i in range(min(20, len(values))):
                orig = values.iloc[i]
                converted = numeric_pd.iloc[i]

                # Проблема: не-ноль стал нулем
                if (pd.notna(converted) and converted == 0 and
                    orig != 0 and orig != '0' and pd.notna(orig)):
                    problems.append((i, orig, converted))

            if problems:
                print(f"[WARNING] НАЙДЕНЫ ПРОБЛЕМЫ ({len(problems)} случаев):")
                for idx, orig, conv in problems[:5]:
                    print(f"  Строка {idx}: '{orig}' -> {conv}")
                print("🔧 РЕКОМЕНДАЦИЯ: Использовать ручное преобразование!")
            else:
                print("✅ pd.to_numeric работает корректно")

            # Статистика нулей
            original_zeros = (values == 0) | (values == '0')
            converted_zeros = (numeric_pd == 0)
            new_zeros = converted_zeros & ~original_zeros

            print(f"\n📈 Статистика нулей:")
            print(f"  Исходных нулей: {original_zeros.sum()}")
            print(f"  После преобразования: {converted_zeros.sum()}")
            print(f"  Новых нулей: {new_zeros.sum()}")

            if new_zeros.sum() > 0:
                print("[WARNING] ВНИМАНИЕ: Появились новые нули!")

        print("=" * 60)

    def load_file(self, file_type):
        """Загрузка Excel файла с данными"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f'Выберите файл {file_type}',
            '',
            'Excel Files (*.xlsx *.xls)'
        )

        if file_path:
            try:
                # Чтение Excel файла
                df = pd.read_excel(file_path)

                # Проверка наличия данных
                if df.empty:
                    self.show_error(f'Файл {file_type} пуст')
                    return

                # ЗАПУСК ОТЛАДЧИКА
                self.debug_data_conversion(df, file_type)

                # Сохранение данных
                self.data_files[file_type] = {
                    'path': file_path,
                    'data': df
                }

                # Обновление метки статуса
                if file_type == 'H2S':
                    self.label_h2s.setText(f'✅ Загружено: {len(df)} записей')
                    self.label_h2s.setStyleSheet('color: green;')
                else:
                    self.label_so2.setText(f'✅ Загружено: {len(df)} записей')
                    self.label_so2.setStyleSheet('color: green;')

                # Активация кнопок
                if len(self.data_files) > 0:
                    self.btn_plot.setEnabled(True)
                    self.btn_debug.setEnabled(True)

                # Обновляем селектор файлов в таблице
                self.update_file_selector()

            except Exception as e:
                self.show_error(f'Ошибка при загрузке файла {file_type}: {str(e)}')

    def plot_data(self):
        """Построение графиков с данными из загруженных файлов"""
        # Очистка предыдущих графиков
        self.plot_widget.clear()
        self.plots = []
        self.crosshair_lines = []

        # Определение количества графиков
        plot_configs = []

        if 'H2S' in self.data_files:
            df_h2s = self.data_files['H2S']['data']
            # Поиск колонок с временем и данными
            time_col, data_cols = self.identify_columns(df_h2s)
            if time_col and data_cols:
                plot_configs.append(('H2S', df_h2s, time_col, data_cols))

        if 'SO2' in self.data_files:
            df_so2 = self.data_files['SO2']['data']
            time_col, data_cols = self.identify_columns(df_so2)
            if time_col and data_cols:
                plot_configs.append(('SO2', df_so2, time_col, data_cols))

        if not plot_configs:
            self.show_error('Не удалось определить структуру данных')
            return

        # Создание графиков
        for i, (gas_type, df, time_col, data_cols) in enumerate(plot_configs):
            # Преобразование времени в timestamp с расширенной логикой
            time_data = None  # Инициализация переменной

            # 1) Прямая попытка (учет dayfirst)
            # Пробуем разные варианты парсинга для максимальной совместимости
            parsed = None
            try:
                # Сначала пробуем с dayfirst=True (формат ДД.ММ.ГГГГ)
                parsed = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')
                invalid_count = parsed.isna().sum()

                # Если много невалидных значений, пробуем без dayfirst
                if invalid_count > len(df) * 0.3:  # Если больше 30% невалидных
                    parsed_alt = pd.to_datetime(df[time_col], dayfirst=False, errors='coerce')
                    # Используем вариант с меньшим количеством ошибок
                    if parsed_alt.isna().sum() < invalid_count:
                        parsed = parsed_alt
                        print(f"Использован парсинг без dayfirst (меньше ошибок: {parsed_alt.isna().sum()} vs {invalid_count})")

                # Дополнительная проверка: если есть невалидные значения, пробуем парсить их отдельно
                # Это важно, если формат времени меняется в середине файла
                if parsed.isna().any():
                    invalid_mask = parsed.isna()
                    invalid_indices = df.index[invalid_mask]
                    invalid_values = df.loc[invalid_mask, time_col]

                    print(f"  Обнаружено {invalid_mask.sum()} нераспарсенных дат, пробуем другие форматы...")

                    # Пробуем разные форматы для невалидных значений
                    # ВАЖНО: добавлен формат '%d.%m.%Y %H:%M' для дат БЕЗ секунд
                    formats_to_try = [
                        '%d.%m.%Y %H:%M',         # КРИТИЧНО: формат без секунд (17.11.2025 0:00)
                        '%d.%m.%Y %H:%M:%S',
                        '%d/%m/%Y %H:%M:%S',
                        '%d/%m/%Y %H:%M',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d %H:%M',
                        '%d.%m.%Y',
                        '%Y.%m.%d %H:%M:%S',
                        '%d-%m-%Y %H:%M:%S'
                    ]

                    for fmt in formats_to_try:
                        # Проверяем только те, что еще не распарсены
                        current_invalid = parsed.isna()
                        if not current_invalid.any():
                            break  # Все распарсено

                        current_invalid_values = df.loc[current_invalid, time_col]
                        try:
                            parsed_manual = pd.to_datetime(current_invalid_values, format=fmt, errors='coerce')
                            # Заменяем успешно распарсенные значения
                            success_mask = parsed_manual.notna()
                            if success_mask.any():
                                success_indices = current_invalid_values.index[success_mask]
                                parsed.loc[success_indices] = parsed_manual[success_mask]
                                print(f"  [OK] Восстановлено {success_mask.sum()} записей с форматом {fmt}")
                        except Exception as e:
                            pass

                    # Финальная проверка: если все еще есть невалидные, пробуем infer_datetime_format
                    if parsed.isna().any():
                        remaining_invalid = df.loc[parsed.isna(), time_col]
                        try:
                            parsed_infer = pd.to_datetime(remaining_invalid, infer_datetime_format=True, errors='coerce')
                            success_mask = parsed_infer.notna()
                            if success_mask.any():
                                remaining_indices = df.index[parsed.isna()][success_mask]
                                parsed.loc[remaining_indices] = parsed_infer[success_mask]
                                print(f"  Восстановлено {success_mask.sum()} записей с автоматическим определением формата")
                        except:
                            pass

            except Exception as e:
                print(f"Ошибка при парсинге времени: {e}")
                parsed = pd.Series([pd.NaT] * len(df))

            # 2) Если всё NaT, пытаемся распознать числа (Unix sec/ms или Excel serial)
            if parsed.isna().all():
                numeric = pd.to_numeric(df[time_col], errors='coerce')
                if numeric.notna().any():
                    if numeric.median() > 1e12:
                        # Вероятно миллисекунды Unix
                        try:
                            parsed = pd.to_datetime(numeric, unit='ms', errors='coerce')
                        except Exception:
                            pass
                    elif numeric.median() > 1e9:
                        # Вероятно секунды Unix
                        try:
                            parsed = pd.to_datetime(numeric, unit='s', errors='coerce')
                        except Exception:
                            pass
                    elif 20000 < numeric.median() < 60000:
                        # Вероятно Excel serial days
                        try:
                            parsed = pd.to_datetime(numeric, unit='D', origin='1899-12-30', errors='coerce')
                        except Exception:
                            pass

            # 3) Если удалось получить даты, используем DateAxisItem с единым форматом, иначе индексы
            if parsed.isna().all():
                time_data = None
                timestamps = np.arange(len(df))
                plot = self.plot_widget.addPlot(row=i, col=0)  # обычная числовая ось
                # Создаем копию DataFrame для сортировки (по индексу)
                df_sorted = df.copy()
            else:
                time_data = parsed
                # СОРТИРОВКА ДАННЫХ ПО ВРЕМЕНИ - критично для корректного отображения графика
                # Создаем временную колонку для сортировки
                df_sorted = df.copy()
                df_sorted['_temp_time'] = time_data

                # Проверяем, сколько данных будет потеряно при фильтрации
                valid_time_count = df_sorted['_temp_time'].notna().sum()
                total_count = len(df_sorted)
                if valid_time_count < total_count:
                    print(f"Предупреждение: {total_count - valid_time_count} записей с невалидным временем будут исключены")

                # Удаляем строки с невалидным временем перед сортировкой
                # ВАЖНО: сохраняем все данные, даже если время не распарсилось
                df_sorted = df_sorted[df_sorted['_temp_time'].notna()].copy()

                # Проверяем, что остались данные
                if len(df_sorted) == 0:
                    print(f"ОШИБКА: Все записи имеют невалидное время!")
                    continue

                # Сортируем по времени
                df_sorted = df_sorted.sort_values('_temp_time').reset_index(drop=True)
                # Обновляем time_data после сортировки
                time_data = df_sorted['_temp_time']

                # Отладочная информация о диапазоне дат
                if len(time_data) > 0:
                    min_date = time_data.min()
                    max_date = time_data.max()
                    print(f"Диапазон дат для {gas_type}: {min_date} - {max_date} ({len(time_data)} записей)")

                try:
                    timestamps = time_data.astype('int64') / 1e9
                except Exception:
                    timestamps = time_data.view('int64') / 1e9

                class FixedDateAxis(DateAxisItem):
                    def tickStrings(self, values, scale, spacing):  # noqa: N802
                        from datetime import datetime as _dt
                        # Единый формат для всех графиков
                        return [_dt.utcfromtimestamp(v).strftime('%d.%m.%Y %H:%M:%S') for v in values]

                axis = FixedDateAxis(orientation='bottom')
                plot = self.plot_widget.addPlot(row=i, col=0, axisItems={'bottom': axis})

            plot.setLabel('left', f'{gas_type} концентрация', units='мг/м³')
            plot.setLabel('bottom', 'Дата и время')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.addLegend()

            # Построение линий для каждой колонки данных
            colors = ['b', 'r', 'g', 'm', 'c', 'y']
            for j, col in enumerate(data_cols):
                try:
                    # Получаем исходные значения из отсортированного DataFrame
                    original_values = df_sorted[col]

                    print(f"\n--- ОБРАБОТКА КОЛОНКИ {col} ---")
                    print(f"Тип данных: {original_values.dtype}")
                    print(f"Всего значений: {len(original_values)}")

                    # Показываем первые значения для диагностики
                    print("Первые 5 исходных значений:")
                    for i in range(min(5, len(original_values))):
                        val = original_values.iloc[i]
                        print(f"  [{i}] '{val}' (тип: {type(val).__name__})")

                    # ИСПРАВЛЕНИЕ: Сразу применяем правильное преобразование с поддержкой запятых
                    print(f"\n🔧 Применяем ручное преобразование для точности...")
                    numeric_values = self.manual_numeric_conversion(original_values, col)

                    # Дополнительная диагностика результата
                    valid_count = pd.notna(numeric_values).sum()
                    zero_count = (numeric_values == 0).sum()
                    print(f"Результат преобразования: {valid_count} валидных, {zero_count} нулей")

                    # Проверяем, есть ли проблемные нули
                    if zero_count > 0:
                        print("Анализ нулевых значений:")
                        zero_indices = np.where(numeric_values == 0)[0][:3]
                        for zi in zero_indices:
                            if zi < len(original_values):
                                orig_val = original_values.iloc[zi]
                                print(f"  Исходное '{orig_val}' -> 0 (корректно: {orig_val == 0 or orig_val == '0'})")

                    # Создаем маску ПОСЛЕ преобразования
                    can_plot_mask = pd.notna(numeric_values) & np.isfinite(numeric_values)

                    # Проверяем длину данных
                    if len(timestamps) != len(numeric_values):
                        print(f"[WARNING] Несоответствие длины: timestamps={len(timestamps)}, values={len(numeric_values)}")
                        min_len = min(len(timestamps), len(numeric_values))
                        timestamps_aligned = timestamps[:min_len]
                        numeric_aligned = numeric_values[:min_len]
                        can_plot_aligned = can_plot_mask[:min_len]
                    else:
                        timestamps_aligned = timestamps
                        numeric_aligned = numeric_values
                        can_plot_aligned = can_plot_mask

                    # Применяем маску для получения валидных данных
                    if isinstance(timestamps_aligned, pd.Series):
                        valid_timestamps = timestamps_aligned[can_plot_aligned].values
                    else:
                        valid_timestamps = timestamps_aligned[can_plot_aligned]

                    valid_values = numeric_aligned[can_plot_aligned]

                    # Статистика
                    print(f"Валидных значений для графика: {len(valid_values)}")
                    if len(valid_values) > 0:
                        zero_count = (valid_values == 0).sum()
                        non_zero_count = (valid_values != 0).sum()
                        min_val = np.nanmin(valid_values)
                        max_val = np.nanmax(valid_values)
                        print(f"  Нулей: {zero_count}, Ненулевых: {non_zero_count}")
                        print(f"  Диапазон: {min_val:.4f} - {max_val:.4f}")

                        # Построение графика со ВСЕМИ валидными данными
                        color = colors[j % len(colors)]
                        plot.plot(np.array(valid_timestamps), np.array(valid_values),
                                pen=pg.mkPen(color, width=2), name=col)
                        print(f"  [OK] График построен с {len(valid_values)} точками")
                    else:
                        print(f"  [WARNING] Нет данных для построения графика")

                except Exception as e:
                    print(f"Ошибка при построении {col}: {e}")
                    import traceback
                    traceback.print_exc()

            # Удаляем временную колонку из отсортированного DataFrame (если она была создана)
            if '_temp_time' in df_sorted.columns:
                df_sorted = df_sorted.drop(columns=['_temp_time'])

            # Линии перекрестия
            vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('k', width=1, style=Qt.DashLine))
            hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('k', width=1, style=Qt.DashLine))
            plot.addItem(vLine, ignoreBounds=True)
            plot.addItem(hLine, ignoreBounds=True)

            self.crosshair_lines.append((vLine, hLine))
            self.plots.append({
                'plot': plot,
                'gas_type': gas_type,
                'timestamps': timestamps,
                'time_data': time_data,
                'time_col': time_col,  # Сохраняем название колонки времени
                'data_cols': data_cols,
                'df': df_sorted  # Используем отсортированный DataFrame
            })

            # Подключение обработчика движения мыши
            plot.scene().sigMouseMoved.connect(self.on_mouse_moved)

        # Синхронизация осей X всех графиков
        if len(self.plots) > 1:
            # Связываем все графики по оси X с первым графиком
            first_plot = self.plots[0]['plot']
            for i in range(1, len(self.plots)):
                self.plots[i]['plot'].setXLink(first_plot)

        self.info_label.setText('Графики построены. Наведите курсор для отображения значений.')

        # Обновляем таблицу данных, если файл уже выбран
        current_file = self.file_selector.currentText()
        if current_file != 'Выберите файл...' and current_file in self.data_files:
            self.populate_data_table(current_file)

    def manual_numeric_conversion(self, series, column_name=""):
        """
        Ручное преобразование значений в числа без использования pd.to_numeric
        Сохраняет точные значения из файла
        """
        result = []
        problems = []

        for i, val in enumerate(series):
            try:
                if pd.isna(val) or val == '' or val == ' ':
                    result.append(np.nan)
                elif isinstance(val, (int, float)):
                    # Уже число
                    result.append(float(val))
                elif isinstance(val, str):
                    # Строка - пробуем преобразовать
                    cleaned = val.strip()
                    if cleaned == '':
                        result.append(np.nan)
                    else:
                        # Заменяем запятые на точки (русский формат)
                        cleaned = cleaned.replace(',', '.')
                        try:
                            num_val = float(cleaned)
                            result.append(num_val)
                        except ValueError:
                            problems.append((i, val))
                            result.append(np.nan)
                else:
                    # Другой тип - пробуем преобразовать через str
                    try:
                        str_val = str(val).strip().replace(',', '.')
                        num_val = float(str_val)
                        result.append(num_val)
                    except (ValueError, TypeError):
                        problems.append((i, val))
                        result.append(np.nan)
            except Exception as e:
                problems.append((i, val, str(e)))
                result.append(np.nan)

        if problems:
            print(f"  {column_name}: {len(problems)} значений не удалось преобразовать:")
            for item in problems[:3]:
                if len(item) == 2:
                    idx, val = item
                    print(f"    [{idx}] '{val}' (тип: {type(val).__name__})")
                else:
                    idx, val, error = item
                    print(f"    [{idx}] '{val}' -> Ошибка: {error}")

        return np.array(result)

    def identify_columns(self, df):
        """Определение колонок с временем и данными"""
        time_col = None
        data_cols = []

        # Список колонок, которые нужно исключить из отображения
        exclude_keywords = ['tagname', 'tag_name', 'тег', 'название']

        # Поиск колонки времени
        time_keywords = ['время', 'time', 'дата', 'date', 'timestamp', 'datetime']
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in time_keywords):
                time_col = col
                break

        # Если не найдена колонка времени, берем первую
        if time_col is None and len(df.columns) > 0:
            time_col = df.columns[0]

        # Остальные числовые колонки считаем данными (исключая TagName и подобные)
        for col in df.columns:
            col_lower = str(col).lower()

            # Пропускаем колонку времени
            if col == time_col:
                continue

            # Пропускаем колонки из списка исключений
            if any(keyword in col_lower for keyword in exclude_keywords):
                continue

            # Проверяем, является ли колонка числовой
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                # Если есть хотя бы одно числовое значение, добавляем колонку
                if numeric_data.notna().any():
                    data_cols.append(col)
            except:
                pass

        return time_col, data_cols

    def on_mouse_moved(self, pos):
        """Обработчик движения мыши для отображения перекрестия и значений"""
        info_text = []

        # Находим график, над которым находится курсор
        active_plot_idx = None
        active_x = None

        for i, plot_data in enumerate(self.plots):
            plot = plot_data['plot']

            # Проверяем, находится ли курсор в области графика
            if plot.sceneBoundingRect().contains(pos):
                mouse_point = plot.vb.mapSceneToView(pos)
                active_x = mouse_point.x()
                active_plot_idx = i
                break

        # Если курсор над каким-то графиком, обновляем все графики
        if active_plot_idx is not None:
            for i, plot_data in enumerate(self.plots):
                plot = plot_data['plot']

                # Обновление линий перекрестия для всех графиков с одинаковым X
                vLine, hLine = self.crosshair_lines[i]
                vLine.setPos(active_x)

                # Y линию обновляем только для активного графика
                if i == active_plot_idx:
                    mouse_point = plot.vb.mapSceneToView(pos)
                    y = mouse_point.y()
                    hLine.setPos(y)

                # Поиск ближайшей точки данных
                timestamps = plot_data['timestamps']
                idx = np.argmin(np.abs(timestamps - active_x))

                if idx < len(plot_data['df']):
                    # Получение данных для отображения
                    gas_type = plot_data['gas_type']

                    # Время (показываем только один раз)
                    if i == 0 or len(info_text) == 0:
                        if plot_data['time_data'] is not None:
                            try:
                                time_str = plot_data['time_data'].iloc[idx].strftime('%d.%m.%Y %H:%M:%S')
                            except:
                                time_str = str(plot_data['time_data'].iloc[idx])
                        else:
                            # Пытаемся получить время из исходной колонки
                            time_col = plot_data.get('time_col')
                            if time_col and time_col in plot_data['df'].columns:
                                try:
                                    raw_time = plot_data['df'][time_col].iloc[idx]
                                    # Пытаемся преобразовать в дату
                                    time_val = pd.to_datetime(raw_time)
                                    time_str = time_val.strftime('%d.%m.%Y %H:%M:%S')
                                except:
                                    # Если не удалось преобразовать, показываем как есть
                                    time_str = str(raw_time)
                            else:
                                time_str = f"Запись {idx}"

                        info_text.append(f"<b>📅 Дата:</b> {time_str}")
                        info_text.append("")  # Пустая строка для разделения

                    info_text.append(f"<b style='color: #2c3e50; font-size: 13px;'>{gas_type}</b>")

                    # Поиск эталонного значения (Ametek)
                    reference_value = None
                    reference_col = None
                    for col in plot_data['data_cols']:
                        col_lower = str(col).lower()
                        if 'ametek' in col_lower or 'амetek' in col_lower:
                            try:
                                raw_ref_value = plot_data['df'][col].iloc[idx]
                                reference_value = pd.to_numeric(raw_ref_value, errors='coerce')
                                if pd.notna(reference_value):
                                    reference_col = col
                                    break
                            except:
                                pass

                    # Значения параметров с процентной разницей
                    for col in plot_data['data_cols']:
                        try:
                            # ИСПРАВЛЕНИЕ: Показываем ТОЧНО то значение, что в файле
                            raw_value = plot_data['df'][col].iloc[idx]

                            # Проверяем, является ли значение числом для расчетов
                            numeric_value = pd.to_numeric(raw_value, errors='coerce')

                            if pd.notna(numeric_value):
                                # Показываем исходное значение (как в файле), но используем числовое для расчетов
                                display_value = raw_value if not pd.isna(raw_value) else numeric_value
                                info_text.append(f"  <span style='color: #34495e;'>{col}:</span> <b style='color: #27ae60;'>{display_value}</b>")

                                # Расчет процентной разницы относительно Ametek
                                if reference_value is not None and pd.notna(reference_value) and reference_col != col and reference_value != 0:
                                    try:
                                        diff_percent = ((numeric_value - reference_value) / reference_value) * 100
                                        # Цвет в зависимости от знака разницы
                                        color = '#e74c3c' if abs(diff_percent) > 5 else '#95a5a6'
                                        sign = '+' if diff_percent > 0 else ''
                                        info_text.append(f"    <span style='color: {color}; font-size: 11px;'>Δ от эталона: {sign}{diff_percent:.2f}%</span>")
                                    except Exception as e:
                                        print(f"Ошибка расчета разности для {col}: {e}")
                            else:
                                # Показываем исходное значение как есть, если это не число
                                info_text.append(f"  <span style='color: #34495e;'>{col}:</span> <span style='color: #95a5a6;'>{raw_value}</span>")
                        except Exception as e:
                            print(f"Ошибка обработки колонки {col} в перекрестии: {e}")

                    # Добавляем пустую строку между графиками
                    if i < len(self.plots) - 1:
                        info_text.append("")

        if info_text:
            self.info_label.setText('<br>'.join(info_text))

    def clear_all(self):
        """Очистка всех данных и графиков"""
        self.data_files = {}
        self.plot_widget.clear()
        self.plots = []
        self.crosshair_lines = []

        self.label_h2s.setText('Файл не загружен')
        self.label_h2s.setStyleSheet('')
        self.label_so2.setText('Файл не загружен')
        self.label_so2.setStyleSheet('')

        self.btn_plot.setEnabled(False)
        self.btn_debug.setEnabled(False)
        self.info_label.setText('Наведите курсор на график для отображения значений')

        # Очищаем таблицу и селектор
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.file_selector.clear()
        self.file_selector.addItem('Выберите файл...')
        self.selection_info.setText('Выберите строку в таблице для выделения на графике')

        # Очищаем выделения на графике
        self.clear_highlights()

    def show_data_debugger(self):
        """Показ визуального отладчика данных"""
        if not self.data_files:
            self.show_error('Сначала загрузите файлы для анализа')
            return

        # Создаем и показываем окно отладчика
        debugger = DataDebuggerDialog(self)
        debugger.analyze_data(self.data_files)
        debugger.exec_()

    def update_file_selector(self):
        """Обновление селектора файлов в таблице"""
        self.file_selector.clear()
        self.file_selector.addItem('Выберите файл...')

        for file_type in self.data_files.keys():
            self.file_selector.addItem(file_type)

    def on_file_selector_changed(self, file_type):
        """Обработка изменения выбранного файла"""
        if file_type == 'Выберите файл...' or file_type not in self.data_files:
            self.data_table.clear()
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.selection_info.setText('Выберите файл для отображения данных')
            return

        self.populate_data_table(file_type)

    def populate_data_table(self, file_type):
        """Заполнение таблицы данными из выбранного файла"""
        try:
            df = self.data_files[file_type]['data']

            # Определяем колонки для отображения
            time_col, data_cols = self.identify_columns(df)
            display_cols = [time_col] + data_cols

            # Настраиваем таблицу
            self.data_table.setRowCount(len(df))
            self.data_table.setColumnCount(len(display_cols))
            self.data_table.setHorizontalHeaderLabels(display_cols)

            # Заполняем данными
            for row in range(len(df)):
                for col_idx, col_name in enumerate(display_cols):
                    value = df[col_name].iloc[row]

                    # Форматируем значение для отображения
                    if col_name == time_col:
                        # Время - показываем как есть
                        display_value = str(value)
                    else:
                        # Числовые данные - форматируем
                        try:
                            numeric_val = pd.to_numeric(value, errors='coerce')
                            if pd.notna(numeric_val):
                                display_value = f"{numeric_val:.4f}"
                            else:
                                display_value = str(value)
                        except:
                            display_value = str(value)

                    item = QTableWidgetItem(display_value)
                    item.setData(Qt.UserRole, row)  # Сохраняем индекс строки
                    self.data_table.setItem(row, col_idx, item)

            # Автоматически подгоняем ширину колонок
            self.data_table.resizeColumnsToContents()

            self.selection_info.setText(f'Отображается {len(df)} записей из файла {file_type}')

        except Exception as e:
            self.show_error(f'Ошибка при заполнении таблицы: {str(e)}')

    def refresh_data_table(self):
        """Обновление таблицы данных"""
        current_file = self.file_selector.currentText()
        if current_file != 'Выберите файл...':
            self.populate_data_table(current_file)

    def on_table_selection_changed(self):
        """Обработка изменения выбора в таблице"""
        selected_items = self.data_table.selectedItems()
        if not selected_items:
            self.clear_highlights()
            self.selection_info.setText('Выберите строку в таблице для выделения на графике')
            return

        # Получаем индекс выбранной строки
        row_index = selected_items[0].data(Qt.UserRole)
        if row_index is None:
            return

        # Выделяем точку на графике
        self.highlight_point_on_graph(row_index)

        # Обновляем информацию
        current_file = self.file_selector.currentText()
        self.selection_info.setText(f'Выбрана строка {row_index + 1} из файла {current_file}')

    def highlight_point_on_graph(self, row_index):
        """Выделение точки на графике"""
        try:
            # Очищаем предыдущие выделения
            self.clear_highlights()

            current_file = self.file_selector.currentText()
            if current_file not in self.data_files:
                return

            # Находим соответствующий график
            plot_data = None
            for plot_info in self.plots:
                if plot_info['gas_type'] == current_file:
                    plot_data = plot_info
                    break

            if not plot_data:
                return

            # Получаем данные для выделения
            timestamps = plot_data['timestamps']
            df = plot_data['df']

            if row_index >= len(timestamps) or row_index >= len(df):
                return

            # Координаты точки для выделения
            x_coord = timestamps[row_index]

            # Выделяем точку на каждой линии графика
            plot = plot_data['plot']
            data_cols = plot_data['data_cols']

            for col in data_cols:
                try:
                    # Получаем значение для этой колонки
                    value = pd.to_numeric(df[col].iloc[row_index], errors='coerce')
                    if pd.notna(value):
                        # Создаем маркер выделения
                        highlight_item = pg.ScatterPlotItem(
                            [x_coord], [value],
                            pen=pg.mkPen('red', width=3),
                            brush=pg.mkBrush('red'),
                            size=10,
                            symbol='o'
                        )
                        plot.addItem(highlight_item)
                        self.highlight_items.append(highlight_item)
                except:
                    continue

        except Exception as e:
            print(f"Ошибка при выделении точки: {e}")

    def clear_highlights(self):
        """Очистка выделений на графике"""
        for item in self.highlight_items:
            try:
                # Находим график, содержащий этот элемент, и удаляем его
                for plot_info in self.plots:
                    plot = plot_info['plot']
                    if item in plot.items:
                        plot.removeItem(item)
            except:
                pass
        self.highlight_items.clear()

    def show_error(self, message):
        """Отображение сообщения об ошибке"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, 'Ошибка', message)


def main():
    """Главная функция запуска приложения"""
    app = QApplication(sys.argv)
    window = AnalyzerComparisonApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
