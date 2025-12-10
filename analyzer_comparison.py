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
                             QTextEdit, QTabWidget, QScrollArea, QFrame, QComboBox,
                             QGroupBox, QLineEdit, QMessageBox, QDateTimeEdit, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from datetime import datetime
import logging
from analyzer_logic import AnalyzerLogic

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analyzer_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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


class ScaleSettingsDialog(QDialog):
    """Диалог настройки шкал приборов и класса точности"""

    def __init__(self, parent=None, current_scales=None):
        super().__init__(parent)
        self.setWindowTitle('Настройки шкал приборов')
        self.setGeometry(300, 300, 600, 400)
        self.current_scales = current_scales or {}
        self.scale_inputs = {}  # Словарь для хранения полей ввода
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса диалога"""
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel('⚙️ НАСТРОЙКА ШКАЛ ПРИБОРОВ И КЛАССА ТОЧНОСТИ')
        title.setStyleSheet('QLabel { font-size: 14px; font-weight: bold; color: #2c3e50; padding: 10px; }')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Инструкция
        instruction = QLabel(
            'Укажите верхний предел измерения (шкалу) и класс точности для каждого анализатора.\n'
            'Класс точности указывается в % от шкалы (например: 1.0 для класса 1.0).'
        )
        instruction.setStyleSheet('QLabel { padding: 5px; color: #7f8c8d; }')
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        # Скроллируемая область для настроек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Получаем список анализаторов из родительского приложения
        if self.parent() and hasattr(self.parent(), 'plots'):
            for plot_data in self.parent().plots:
                gas_type = plot_data['gas_type']
                data_cols = plot_data['data_cols']

                # Группа для газа
                gas_group = QGroupBox(f'📊 {gas_type}')
                gas_group.setStyleSheet('QGroupBox { font-weight: bold; padding: 10px; }')
                gas_layout = QVBoxLayout()

                if gas_type not in self.scale_inputs:
                    self.scale_inputs[gas_type] = {}

                for analyzer in data_cols:
                    # Строка для каждого анализатора
                    analyzer_layout = QHBoxLayout()

                    # Название анализатора
                    name_label = QLabel(analyzer)
                    name_label.setMinimumWidth(150)
                    name_label.setStyleSheet('QLabel { font-size: 11px; }')
                    analyzer_layout.addWidget(name_label)

                    # Поле ввода шкалы
                    scale_label = QLabel('Шкала (мг/м³):')
                    analyzer_layout.addWidget(scale_label)

                    scale_input = QLineEdit()
                    scale_input.setPlaceholderText('100.0')
                    scale_input.setMaximumWidth(80)

                    # Загружаем сохраненное значение, если есть
                    if gas_type in self.current_scales and analyzer in self.current_scales[gas_type]:
                        scale_val = self.current_scales[gas_type][analyzer].get('scale', '')
                        if scale_val:
                            scale_input.setText(str(scale_val))

                    analyzer_layout.addWidget(scale_input)

                    # Поле ввода класса точности
                    accuracy_label = QLabel('Класс точности (%):')
                    analyzer_layout.addWidget(accuracy_label)

                    accuracy_input = QLineEdit()
                    accuracy_input.setPlaceholderText('1.0')
                    accuracy_input.setMaximumWidth(80)

                    # Загружаем сохраненное значение, если есть
                    if gas_type in self.current_scales and analyzer in self.current_scales[gas_type]:
                        accuracy_val = self.current_scales[gas_type][analyzer].get('accuracy_class', '')
                        if accuracy_val:
                            accuracy_input.setText(str(accuracy_val))

                    analyzer_layout.addWidget(accuracy_input)

                    analyzer_layout.addStretch()

                    gas_layout.addLayout(analyzer_layout)

                    # Сохраняем ссылки на поля ввода
                    self.scale_inputs[gas_type][analyzer] = {
                        'scale': scale_input,
                        'accuracy': accuracy_input
                    }

                gas_group.setLayout(gas_layout)
                scroll_layout.addWidget(gas_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton('💾 Сохранить')
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet(
            'QPushButton { padding: 8px; font-size: 11px; background-color: #27ae60; color: white; }'
        )
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton('❌ Отмена')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet('QPushButton { padding: 8px; font-size: 11px; }')
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def save_settings(self):
        """Сохранение настроек"""
        from PyQt5.QtWidgets import QMessageBox

        result = {}
        errors = []

        for gas_type, analyzers in self.scale_inputs.items():
            result[gas_type] = {}

            for analyzer, inputs in analyzers.items():
                scale_text = inputs['scale'].text().strip()
                accuracy_text = inputs['accuracy'].text().strip()

                # Пропускаем пустые поля
                if not scale_text and not accuracy_text:
                    continue

                try:
                    scale = float(scale_text.replace(',', '.')) if scale_text else None
                    accuracy = float(accuracy_text.replace(',', '.')) if accuracy_text else None

                    if scale is not None and scale <= 0:
                        errors.append(f'{gas_type} - {analyzer}: шкала должна быть положительной')
                        continue

                    if accuracy is not None and (accuracy <= 0 or accuracy > 100):
                        errors.append(f'{gas_type} - {analyzer}: класс точности должен быть от 0 до 100%')
                        continue

                    result[gas_type][analyzer] = {
                        'scale': scale,
                        'accuracy_class': accuracy
                    }

                except ValueError:
                    errors.append(f'{gas_type} - {analyzer}: некорректное числовое значение')

        if errors:
            QMessageBox.warning(self, 'Ошибки ввода', '\n'.join(errors))
            return

        self.result_scales = result
        self.accept()

    def get_scales(self):
        """Получить настроенные шкалы"""
        return getattr(self, 'result_scales', {})


class AnalyzerComparisonApp(QMainWindow):
    """Главное окно приложения для сравнения анализаторов"""

    def __init__(self):
        super().__init__()
        self.data_files = {}  # Словарь для хранения загруженных данных
        self.plots = []  # Список графиков
        self.crosshair_lines = []  # Линии перекрестия
        self.value_labels = []  # Метки для отображения значений
        self.highlight_items = []  # Элементы выделения на графике

        # Состояние режима выборки диапазона
        self.selection_mode = False  # Флаг режима выборки
        self.selection_regions = []  # Список LinearRegionItem объектов
        self.selection_results = {}  # Результаты расчетов {plot_index: results_dict}
        self.original_mouse_handlers = []  # Оригинальные обработчики событий
        self.current_selection_region = None  # Временная переменная при создании
        self.selection_start_x = None  # Начало выделения
        self.selection_plot_index = None  # Индекс активного графика

        # Режим фильтрации выбросов (замена 0 и 1 на предыдущие значения)
        self.filter_outliers_mode = False  # Флаг режима фильтрации

        # Временное хранилище регионов при создании выделения
        self.temp_selection_regions = []

        # Настройки шкал приборов и погрешностей
        # Формат: {gas_type: {analyzer_name: {'scale': float, 'accuracy_class': float}}}
        self.analyzer_scales = {}

        # Настройки диапазона времени для графиков
        self.date_range_enabled = False  # Флаг использования диапазона
        self.date_range_start = None  # Начало диапазона
        self.date_range_end = None  # Конец диапазона

        # Инициализация логики
        self.logic = AnalyzerLogic()

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

        # Панель выбора диапазона дат
        date_range_panel = self.create_date_range_panel()
        main_layout.addWidget(date_range_panel)

        # Панель информации (метки для отображения значений при перекрестии)
        self.info_label = QLabel('Наведите курсор на график для отображения значений')
        self.info_label.setStyleSheet('QLabel { background-color: #f0f0f0; padding: 8px; font-size: 11px; border: 1px solid #d0d0d0; }')
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.info_label.setMinimumHeight(140)
        self.info_label.setMaximumHeight(200)
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

        # Кнопка фильтрации выбросов
        self.btn_filter_outliers = QPushButton('🔧 Фильтр выбросов (0/1)')
        self.btn_filter_outliers.setCheckable(True)
        self.btn_filter_outliers.setChecked(False)
        self.btn_filter_outliers.toggled.connect(self.toggle_filter_outliers)
        self.btn_filter_outliers.setEnabled(False)
        self.btn_filter_outliers.setStyleSheet(self.get_filter_button_style(False))
        self.btn_filter_outliers.setToolTip('Заменять нули и единицы на предыдущие значения (для устранения выбросов при обрыве связи)')
        layout.addWidget(self.btn_filter_outliers)

        # Кнопка настройки шкал приборов
        self.btn_scale_settings = QPushButton('⚙️ Шкалы приборов')
        self.btn_scale_settings.clicked.connect(self.open_scale_settings)
        self.btn_scale_settings.setEnabled(False)
        self.btn_scale_settings.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; background-color: #9C27B0; color: white; } QPushButton:disabled { background-color: #cccccc; }')
        self.btn_scale_settings.setToolTip('Настроить шкалы и класс точности приборов для расчета приведенной погрешности')
        layout.addWidget(self.btn_scale_settings)

        layout.addStretch()

        # Кнопка режима выборки
        self.btn_selection_mode = QPushButton('🎯 Режим выборки')
        self.btn_selection_mode.setCheckable(True)
        self.btn_selection_mode.setChecked(False)
        self.btn_selection_mode.toggled.connect(self.toggle_selection_mode)
        self.btn_selection_mode.setEnabled(False)
        self.btn_selection_mode.setStyleSheet(self.get_button_style(False))
        layout.addWidget(self.btn_selection_mode)

        # Кнопка очистки выборки
        self.btn_clear_selection = QPushButton('🗑️ Очистить выборку')
        self.btn_clear_selection.clicked.connect(self.clear_all_selections)
        self.btn_clear_selection.setEnabled(False)
        self.btn_clear_selection.setStyleSheet('QPushButton { padding: 4px; font-size: 10px; }')
        layout.addWidget(self.btn_clear_selection)

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

    def create_date_range_panel(self):
        """Создание панели выбора диапазона дат и времени для графиков"""
        panel = QWidget()
        panel.setStyleSheet('QWidget { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 5px; }')
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        # Чекбокс для включения/отключения фильтрации по диапазону
        self.date_range_checkbox = QCheckBox('📅 Диапазон дат:')
        self.date_range_checkbox.setStyleSheet('QCheckBox { font-size: 11px; font-weight: bold; }')
        self.date_range_checkbox.toggled.connect(self.toggle_date_range)
        layout.addWidget(self.date_range_checkbox)

        # Метка "С:"
        label_from = QLabel('С:')
        label_from.setStyleSheet('QLabel { font-size: 11px; margin-left: 10px; }')
        layout.addWidget(label_from)

        # Виджет выбора начальной даты и времени
        self.date_start = QDateTimeEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat('dd.MM.yyyy HH:mm')
        self.date_start.setEnabled(False)
        self.date_start.setStyleSheet('QDateTimeEdit { font-size: 10px; padding: 3px; }')
        self.date_start.dateTimeChanged.connect(self.on_date_range_changed)
        layout.addWidget(self.date_start)

        # Метка "По:"
        label_to = QLabel('По:')
        label_to.setStyleSheet('QLabel { font-size: 11px; margin-left: 10px; }')
        layout.addWidget(label_to)

        # Виджет выбора конечной даты и времени
        self.date_end = QDateTimeEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat('dd.MM.yyyy HH:mm')
        self.date_end.setEnabled(False)
        self.date_end.setStyleSheet('QDateTimeEdit { font-size: 10px; padding: 3px; }')
        self.date_end.dateTimeChanged.connect(self.on_date_range_changed)
        layout.addWidget(self.date_end)

        # Кнопка сброса диапазона
        self.btn_reset_range = QPushButton('🔄 Сбросить')
        self.btn_reset_range.setEnabled(False)
        self.btn_reset_range.clicked.connect(self.reset_date_range)
        self.btn_reset_range.setStyleSheet('QPushButton { padding: 5px; font-size: 10px; margin-left: 10px; }')
        self.btn_reset_range.setToolTip('Сбросить диапазон и показать все данные')
        layout.addWidget(self.btn_reset_range)

        # Кнопка применения диапазона
        self.btn_apply_range = QPushButton('✓ Применить')
        self.btn_apply_range.setEnabled(False)
        self.btn_apply_range.clicked.connect(self.apply_date_range)
        self.btn_apply_range.setStyleSheet('QPushButton { padding: 5px; font-size: 10px; background-color: #28a745; color: white; } QPushButton:disabled { background-color: #cccccc; }')
        self.btn_apply_range.setToolTip('Применить выбранный диапазон к графикам')
        layout.addWidget(self.btn_apply_range)

        # Метка информации о диапазоне
        self.date_range_info = QLabel('Выберите файлы и постройте графики для выбора диапазона')
        self.date_range_info.setStyleSheet('QLabel { color: #6c757d; font-size: 10px; margin-left: 10px; }')
        layout.addWidget(self.date_range_info)

        layout.addStretch()

        return panel

    def toggle_date_range(self, checked):
        """Включение/отключение фильтрации по диапазону дат"""
        self.date_start.setEnabled(checked)
        self.date_end.setEnabled(checked)
        self.btn_apply_range.setEnabled(checked and len(self.plots) > 0)
        self.btn_reset_range.setEnabled(checked)

        if not checked:
            # Если диапазон отключен, сбрасываем его
            self.date_range_enabled = False
            self.date_range_info.setText('Диапазон дат отключен')
            self.date_range_info.setStyleSheet('QLabel { color: #6c757d; font-size: 10px; margin-left: 10px; }')
        else:
            self.date_range_info.setText('Выберите диапазон дат и нажмите "Применить"')
            self.date_range_info.setStyleSheet('QLabel { color: #007bff; font-size: 10px; margin-left: 10px; }')

    def on_date_range_changed(self):
        """Обработчик изменения диапазона дат"""
        if self.date_range_checkbox.isChecked():
            start = self.date_start.dateTime().toPyDateTime()
            end = self.date_end.dateTime().toPyDateTime()

            if start >= end:
                self.date_range_info.setText('⚠️ Начальная дата должна быть меньше конечной!')
                self.date_range_info.setStyleSheet('QLabel { color: #dc3545; font-size: 10px; margin-left: 10px; font-weight: bold; }')
                self.btn_apply_range.setEnabled(False)
            else:
                self.date_range_info.setText(f'Выбран диапазон: {start.strftime("%d.%m.%Y %H:%M")} - {end.strftime("%d.%m.%Y %H:%M")}')
                self.date_range_info.setStyleSheet('QLabel { color: #28a745; font-size: 10px; margin-left: 10px; }')
                self.btn_apply_range.setEnabled(True)

    def reset_date_range(self):
        """Сброс диапазона дат и отображение всех данных"""
        self.date_range_enabled = False
        self.date_range_checkbox.setChecked(False)
        self.date_range_info.setText('Диапазон сброшен. Нажмите "Построить графики" для обновления')
        self.date_range_info.setStyleSheet('QLabel { color: #28a745; font-size: 10px; margin-left: 10px; }')

        # Автоматически перестроить графики если они уже были построены
        if len(self.plots) > 0:
            self.plot_data()

    def apply_date_range(self):
        """Применение выбранного диапазона дат"""
        if not self.date_range_checkbox.isChecked():
            return

        start = self.date_start.dateTime().toPyDateTime()
        end = self.date_end.dateTime().toPyDateTime()

        if start >= end:
            QMessageBox.warning(self, 'Ошибка', 'Начальная дата должна быть меньше конечной!')
            return

        self.date_range_enabled = True
        self.date_range_start = pd.Timestamp(start)
        self.date_range_end = pd.Timestamp(end)

        self.date_range_info.setText(f'✓ Применен диапазон: {start.strftime("%d.%m.%Y %H:%M")} - {end.strftime("%d.%m.%Y %H:%M")}')
        self.date_range_info.setStyleSheet('QLabel { color: #28a745; font-size: 10px; margin-left: 10px; font-weight: bold; }')

        # Перестроить графики с новым диапазоном
        self.plot_data()

    def update_date_range_limits(self):
        """Обновление пределов выбора дат на основе загруженных данных"""
        if not self.data_files:
            return

        min_date = None
        max_date = None

        # Находим минимальную и максимальную даты во всех файлах
        for file_type, file_data in self.data_files.items():
            # Используем уже распарсенные даты
            time_data = file_data.get('parsed_dates')
            
            if time_data is not None and not time_data.isna().all():
                file_min = time_data.min()
                file_max = time_data.max()

                if pd.notna(file_min):
                    if min_date is None or file_min < min_date:
                        min_date = file_min

                if pd.notna(file_max):
                    if max_date is None or file_max > max_date:
                        max_date = file_max

        if min_date and max_date:
            # Устанавливаем пределы для виджетов выбора дат
            from PyQt5.QtCore import QDateTime

            self.date_start.setDateTimeRange(
                QDateTime(min_date.year, min_date.month, min_date.day,
                         min_date.hour, min_date.minute),
                QDateTime(max_date.year, max_date.month, max_date.day,
                         max_date.hour, max_date.minute)
            )

            self.date_end.setDateTimeRange(
                QDateTime(min_date.year, min_date.month, min_date.day,
                         min_date.hour, min_date.minute),
                QDateTime(max_date.year, max_date.month, max_date.day,
                         max_date.hour, max_date.minute)
            )

            # Устанавливаем начальные значения
            self.date_start.setDateTime(
                QDateTime(min_date.year, min_date.month, min_date.day,
                         min_date.hour, min_date.minute)
            )

            self.date_end.setDateTime(
                QDateTime(max_date.year, max_date.month, max_date.day,
                         max_date.hour, max_date.minute)
            )

            self.date_range_info.setText(
                f'Доступный диапазон: {min_date.strftime("%d.%m.%Y %H:%M")} - {max_date.strftime("%d.%m.%Y %H:%M")}'
            )
            self.date_range_info.setStyleSheet('QLabel { color: #007bff; font-size: 10px; margin-left: 10px; }')

    def debug_data_conversion(self, df, file_type):
        """ОТЛАДЧИК: Анализ преобразования данных из Excel файла"""
        print(f"\n[DEBUG] ОТЛАДЧИК ДАННЫХ - {file_type}")
        print("=" * 60)

        # Определяем колонки данных
        time_col, data_cols = self.logic.identify_columns(df)

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

                # Определяем колонки
                time_col, data_cols = self.logic.identify_columns(df)
                
                # Парсим даты сразу при загрузке
                parsed_dates = None
                if time_col:
                    logger.info(f"Парсинг дат для {file_type} (колонка {time_col})...")
                    parsed_dates = self.logic.parse_dates(df[time_col])
                    valid_dates = parsed_dates.notna().sum()
                    logger.info(f"Успешно распарсено дат: {valid_dates}/{len(df)}")

                # Сохранение данных
                self.data_files[file_type] = {
                    'path': file_path,
                    'data': df,
                    'time_col': time_col,
                    'data_cols': data_cols,
                    'parsed_dates': parsed_dates
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
                    self.btn_filter_outliers.setEnabled(True)

                # Обновляем селектор файлов в таблице
                self.update_file_selector()

                # Обновляем доступные диапазоны дат
                self.update_date_range_limits()

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

        for gas_type in ['H2S', 'SO2']:
            if gas_type in self.data_files:
                file_data = self.data_files[gas_type]
                df = file_data['data']
                time_col = file_data.get('time_col')
                data_cols = file_data.get('data_cols')
                parsed_dates = file_data.get('parsed_dates')
                
                if time_col and data_cols:
                    plot_configs.append((gas_type, df, time_col, data_cols, parsed_dates))

        if not plot_configs:
            self.show_error('Не удалось определить структуру данных')
            return

        # Создание графиков
        for i, (gas_type, df, time_col, data_cols, parsed_dates) in enumerate(plot_configs):
            # Используем распарсенные даты
            time_data = parsed_dates
            
            # СОРТИРОВКА ДАННЫХ ПО ВРЕМЕНИ
            if time_data is not None:
                # Создаем временную колонку для сортировки
                df_sorted = df.copy()
                df_sorted['_temp_time'] = time_data

                # Удаляем строки с невалидным временем
                df_sorted = df_sorted[df_sorted['_temp_time'].notna()].copy()

                if len(df_sorted) == 0:
                    logger.error(f"Все записи для {gas_type} имеют невалидное время!")
                    continue

                # Сортируем
                df_sorted = df_sorted.sort_values('_temp_time').reset_index(drop=True)
                time_data = df_sorted['_temp_time']

                # Фильтрация по диапазону
                if self.date_range_enabled and self.date_range_start and self.date_range_end:
                    logger.info(f"Применяем фильтр дат: {self.date_range_start} - {self.date_range_end}")
                    date_mask = (time_data >= self.date_range_start) & (time_data <= self.date_range_end)
                    df_sorted = df_sorted[date_mask].reset_index(drop=True)
                    time_data = df_sorted['_temp_time']

                    if len(df_sorted) == 0:
                        logger.warning(f"После фильтрации нет данных для {gas_type}")
                        continue

                try:
                    timestamps = time_data.astype('int64') / 1e9
                except:
                    timestamps = time_data.view('int64') / 1e9

                class FixedDateAxis(DateAxisItem):
                    def tickStrings(self, values, scale, spacing):  # noqa: N802
                        from datetime import datetime as _dt
                        return [_dt.utcfromtimestamp(v).strftime('%d.%m.%Y %H:%M:%S') for v in values]

                axis = FixedDateAxis(orientation='bottom')
                plot = self.plot_widget.addPlot(row=i, col=0, axisItems={'bottom': axis})
            else:
                # Если дат нет, используем индексы
                time_data = None
                timestamps = np.arange(len(df))
                plot = self.plot_widget.addPlot(row=i, col=0)
                df_sorted = df.copy()

            plot.setLabel('left', f'{gas_type} концентрация', units='мг/м³')
            plot.setLabel('bottom', 'Дата и время')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.addLegend()

            # Словарь для хранения отфильтрованных данных
            current_filtered_data = {}

            # Построение линий
            colors = ['b', 'r', 'g', 'm', 'c', 'y']
            for j, col in enumerate(data_cols):
                try:
                    original_values = df_sorted[col]
                    
                    # Используем логику для преобразования (векторизованно)
                    numeric_values = self.logic.manual_numeric_conversion(original_values)

                    # Фильтр выбросов
                    if self.filter_outliers_mode:
                        numeric_values = self.logic.apply_outlier_filter(numeric_values)

                    current_filtered_data[col] = numeric_values

                    # Маска валидных данных
                    can_plot_mask = pd.notna(numeric_values) & np.isfinite(numeric_values)
                    
                    # Выравнивание длин
                    if len(timestamps) != len(numeric_values):
                        min_len = min(len(timestamps), len(numeric_values))
                        timestamps_aligned = timestamps[:min_len]
                        numeric_aligned = numeric_values[:min_len]
                        can_plot_aligned = can_plot_mask[:min_len]
                    else:
                        timestamps_aligned = timestamps
                        numeric_aligned = numeric_values
                        can_plot_aligned = can_plot_mask

                    if isinstance(timestamps_aligned, pd.Series):
                        valid_timestamps = timestamps_aligned[can_plot_aligned].values
                    else:
                        valid_timestamps = timestamps_aligned[can_plot_aligned]
                        
                    valid_values = numeric_aligned[can_plot_aligned]

                    if len(valid_values) > 0:
                        color = colors[j % len(colors)]
                        plot.plot(np.array(valid_timestamps), np.array(valid_values),
                                pen=pg.mkPen(color, width=2), name=col)
                    else:
                        logger.warning(f"Нет валидных данных для {col}")

                except Exception as e:
                    logger.error(f"Ошибка построения {col}: {e}")

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
                'time_col': time_col,
                'data_cols': data_cols,
                'df': df_sorted,
                'filtered_data': current_filtered_data
            })

            plot.scene().sigMouseMoved.connect(self.on_mouse_moved)

        # Синхронизация осей
        if len(self.plots) > 1:
            first_plot = self.plots[0]['plot']
            for i in range(1, len(self.plots)):
                self.plots[i]['plot'].setXLink(first_plot)

        self.info_label.setText('Графики построены. Наведите курсор для отображения значений.')

        if len(self.plots) > 0:
            self.btn_selection_mode.setEnabled(True)
            self.btn_clear_selection.setEnabled(False)
            self.btn_scale_settings.setEnabled(True)

        self.clear_all_selections()
        if self.selection_mode:
            self.enable_selection_mode()

        current_file = self.file_selector.currentText()
        if current_file != 'Выберите файл...' and current_file in self.data_files:
            self.populate_data_table(current_file)


    def on_mouse_moved(self, pos):
        """Обработчик движения мыши для отображения перекрестия и значений"""
        # Если активен режим выборки и есть результаты - не обновляем info_label
        if self.selection_mode and len(self.selection_results) > 0:
            return

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

                    # Получаем отфильтрованные данные, если они есть
                    filtered_data = plot_data.get('filtered_data', {})

                    # Поиск эталонного значения (Ametek) из отфильтрованных данных
                    reference_value = None
                    reference_col = None
                    for col in plot_data['data_cols']:
                        col_lower = str(col).lower()
                        if 'ametek' in col_lower or 'амetek' in col_lower:
                            try:
                                # Используем отфильтрованные данные, если они есть
                                if col in filtered_data and len(filtered_data[col]) > idx:
                                    reference_value = filtered_data[col][idx]
                                else:
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
                            # Используем отфильтрованные данные, если они есть
                            if col in filtered_data and len(filtered_data[col]) > idx:
                                numeric_value = filtered_data[col][idx]
                                # Показываем отфильтрованное значение
                                display_value = numeric_value
                            else:
                                # Иначе берем из исходного DataFrame
                                raw_value = plot_data['df'][col].iloc[idx]
                                numeric_value = pd.to_numeric(raw_value, errors='coerce')
                                display_value = raw_value if not pd.isna(raw_value) else numeric_value

                            if pd.notna(numeric_value):
                                # Форматируем значение для отображения
                                if isinstance(display_value, (int, float, np.number)):
                                    display_str = f"{display_value:.4f}" if display_value != int(display_value) else f"{int(display_value)}"
                                else:
                                    display_str = str(display_value)

                                info_text.append(f"  <span style='color: #34495e;'>{col}:</span> <b style='color: #27ae60;'>{display_str}</b>")

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
                                # Показываем как N/A, если это не число
                                info_text.append(f"  <span style='color: #34495e;'>{col}:</span> <span style='color: #95a5a6;'>N/A</span>")
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
        self.btn_filter_outliers.setEnabled(False)
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

        # Очистка выделений диапазона
        self.clear_all_selections()

        # Выход из режима выборки
        if self.selection_mode:
            self.btn_selection_mode.setChecked(False)
            self.toggle_selection_mode(False)

        # Деактивация кнопок выборки
        self.btn_selection_mode.setEnabled(False)
        self.btn_clear_selection.setEnabled(False)

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

    # ==================== МЕТОДЫ ФИЛЬТРАЦИИ ВЫБРОСОВ ====================

    def get_filter_button_style(self, active):
        """Получить стиль для кнопки фильтрации выбросов"""
        if active:
            return '''
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    padding: 8px;
                    font-size: 11px;
                    border: 2px solid #d35400;
                    font-weight: bold;
                }
            '''
        else:
            return '''
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    padding: 8px;
                    font-size: 11px;
                    border: 2px solid #bdc3c7;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #7f8c8d;
                }
            '''

    def toggle_filter_outliers(self, checked):
        """Переключение режима фильтрации выбросов"""
        self.filter_outliers_mode = checked

        # Обновить внешний вид кнопки
        self.btn_filter_outliers.setStyleSheet(self.get_filter_button_style(checked))

        if checked:
            self.btn_filter_outliers.setText('🔧 Фильтр выбросов (ВКЛ)')
            print("\n[FILTER] Режим фильтрации выбросов ВКЛЮЧЕН")
            print("[FILTER] Нули и единицы будут заменены на предыдущие значения")
        else:
            self.btn_filter_outliers.setText('🔧 Фильтр выбросов (0/1)')
            print("\n[FILTER] Режим фильтрации выбросов ВЫКЛЮЧЕН")

        # Автоматически перестроить графики, если данные загружены
        if len(self.plots) > 0:
            print("[FILTER] Перестроение графиков с новыми настройками...")
            self.plot_data()


    def open_scale_settings(self):
        """Открыть диалог настройки шкал приборов"""
        dialog = ScaleSettingsDialog(self, self.analyzer_scales)
        if dialog.exec_() == QDialog.Accepted:
            self.analyzer_scales = dialog.get_scales()
            print("\n[SCALES] Настройки шкал приборов обновлены:")
            for gas_type, analyzers in self.analyzer_scales.items():
                print(f"  {gas_type}:")
                for analyzer, settings in analyzers.items():
                    scale = settings.get('scale', 'не указано')
                    accuracy = settings.get('accuracy_class', 'не указано')
                    print(f"    {analyzer}: шкала={scale} мг/м³, класс точности={accuracy}%")

    # ==================== МЕТОДЫ ВЫБОРКИ ДИАПАЗОНА ====================

    def get_button_style(self, active):
        """Получить стиль для кнопки режима выборки в зависимости от состояния"""
        if active:
            return '''
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 8px;
                    font-size: 11px;
                    border: 2px solid #2980b9;
                    font-weight: bold;
                }
            '''
        else:
            return '''
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    padding: 8px;
                    font-size: 11px;
                    border: 2px solid #bdc3c7;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #7f8c8d;
                }
            '''

    def toggle_selection_mode(self, checked):
        """Переключение режима выборки"""
        self.selection_mode = checked

        # Обновить внешний вид кнопки
        self.btn_selection_mode.setStyleSheet(self.get_button_style(checked))

        if checked:
            # Вход в режим выборки
            self.btn_selection_mode.setText('🎯 Режим выборки (активен)')
            # Показываем результаты если они есть, иначе инструкцию
            if len(self.selection_results) == 0:
                self.info_label.setText(
                    '<b style="color: #3498db;">🎯 РЕЖИМ ВЫБОРКИ АКТИВЕН</b><br>'
                    'Перетащите мышью на графике для выбора диапазона.<br>'
                    'Нажмите кнопку снова для выхода из режима.'
                )
            self.enable_selection_mode()
        else:
            # Выход из режима выборки
            self.btn_selection_mode.setText('🎯 Режим выборки')
            self.info_label.setText(
                'Режим выборки отключен. '
                'Наведите курсор на график для отображения значений.'
            )
            self.disable_selection_mode()

    def enable_selection_mode(self):
        """Активация режима выборки на всех графиках"""
        # Защита от повторной инициализации
        if len(self.original_mouse_handlers) > 0:
            print("[SELECTION] Обработчики уже установлены, пропускаем")
            return

        print(f"[SELECTION] Устанавливаем обработчики для {len(self.plots)} графиков")

        for i, plot_data in enumerate(self.plots):
            plot = plot_data['plot']
            vb = plot.vb

            # Сохранить оригинальные обработчики событий мыши и режим мыши
            self.original_mouse_handlers.append({
                'plot_index': i,
                'press': vb.mousePressEvent,
                'move': vb.mouseMoveEvent,
                'release': vb.mouseReleaseEvent,
                'mouseEnabled': (vb.state['mouseEnabled'][0], vb.state['mouseEnabled'][1])
            })

            # Создаём обёртки, которые НЕ вызывают оригинальные обработчики
            def make_press_handler(idx):
                original_handler = vb.mousePressEvent
                def handler(evt):
                    print(f"[SELECTION] Press event на графике {idx}, mode={self.selection_mode}")
                    if self.selection_mode:
                        self.selection_mouse_press(evt, idx)
                    else:
                        original_handler(evt)
                return handler

            def make_move_handler(idx):
                original_handler = vb.mouseMoveEvent
                def handler(evt):
                    if self.selection_mode:
                        self.selection_mouse_move(evt, idx)
                    else:
                        original_handler(evt)
                return handler

            def make_release_handler(idx):
                original_handler = vb.mouseReleaseEvent
                def handler(evt):
                    print(f"[SELECTION] Release event на графике {idx}, mode={self.selection_mode}")
                    if self.selection_mode:
                        self.selection_mouse_release(evt, idx)
                    else:
                        original_handler(evt)
                return handler

            # Установить кастомные обработчики
            vb.mousePressEvent = make_press_handler(i)
            vb.mouseMoveEvent = make_move_handler(i)
            vb.mouseReleaseEvent = make_release_handler(i)

            print(f"[SELECTION] Обработчики установлены для графика {i}")

    def disable_selection_mode(self):
        """Деактивация режима выборки и восстановление обычного поведения"""
        # Восстановить оригинальные обработчики событий
        for handler_info in self.original_mouse_handlers:
            idx = handler_info['plot_index']
            if idx < len(self.plots):
                plot = self.plots[idx]['plot']
                vb = plot.vb

                vb.mousePressEvent = handler_info['press']
                vb.mouseMoveEvent = handler_info['move']
                vb.mouseReleaseEvent = handler_info['release']

        self.original_mouse_handlers.clear()

    def selection_mouse_press(self, evt, plot_index):
        """Обработчик нажатия мыши в режиме выборки"""
        if not self.selection_mode:
            return

        if evt.button() == Qt.LeftButton:
            # Принять событие только для левой кнопки
            evt.accept()

            # Получить позицию мыши в координатах графика
            plot_data = self.plots[plot_index]
            plot = plot_data['plot']
            pos = evt.pos()
            mouse_point = plot.vb.mapToView(pos)

            # Сохранить начальную позицию
            self.selection_start_x = mouse_point.x()
            self.selection_plot_index = plot_index

            print(f"[SELECTION] Начало выборки на графике {plot_index}, X={self.selection_start_x}")

            # Очистить предыдущие выделения на ВСЕХ графиках
            self.clear_all_selections()

            # Создать области выделения на ВСЕХ графиках
            for i in range(len(self.plots)):
                region = self.create_selection_region(i, self.selection_start_x, self.selection_start_x)
                print(f"[SELECTION] Создан регион на графике {i}")

    def selection_mouse_move(self, evt, plot_index):
        """Обработчик движения мыши в режиме выборки"""
        if not self.selection_mode or self.selection_start_x is None:
            return

        if plot_index != self.selection_plot_index:
            return

        # Принять событие
        evt.accept()

        # Обновить область выделения
        plot_data = self.plots[plot_index]
        plot = plot_data['plot']
        pos = evt.pos()
        mouse_point = plot.vb.mapToView(pos)
        current_x = mouse_point.x()

        # Обновить границы LinearRegionItem на ВСЕХ графиках
        updated_count = 0
        for i, plot_info in enumerate(self.plots):
            plot_obj = plot_info['plot']
            # Найти LinearRegionItem для этого графика
            for item in plot_obj.items:
                if isinstance(item, pg.LinearRegionItem):
                    item.setRegion([self.selection_start_x, current_x])
                    updated_count += 1
                    break

        if updated_count == 0:
            print(f"[WARNING] Не найдено LinearRegionItem для обновления!")

    def selection_mouse_release(self, evt, plot_index):
        """Обработчик отпускания мыши - завершение выделения"""
        if not self.selection_mode or self.selection_start_x is None:
            return

        # Принять событие, чтобы оно не передавалось дальше
        evt.accept()

        if evt.button() == Qt.LeftButton and plot_index == self.selection_plot_index:
            # Получить финальную позицию
            plot_data = self.plots[plot_index]
            plot = plot_data['plot']
            pos = evt.pos()
            mouse_point = plot.vb.mapToView(pos)
            end_x = mouse_point.x()

            # Убедиться что start < end
            x_start = min(self.selection_start_x, end_x)
            x_end = max(self.selection_start_x, end_x)

            # Валидация: проверить минимальную ширину
            if abs(x_end - x_start) < 1e-6:
                # Слишком маленькое выделение, игнорировать
                self.clear_all_selections()
                self.info_label.setText(
                    '<span style="color: #e74c3c;">Выбор слишком мал. '
                    'Попробуйте еще раз.</span>'
                )
            else:
                # Обработать выделение для ВСЕХ графиков и рассчитать результаты
                self.process_all_selections(x_start, x_end)

            # Очистить временные переменные
            self.selection_start_x = None
            self.selection_plot_index = None

    def create_selection_region(self, plot_index, x_start, x_end):
        """Создать LinearRegionItem для визуального выделения"""
        plot = self.plots[plot_index]['plot']

        # Создать область выделения
        region = pg.LinearRegionItem(
            values=[x_start, x_end],
            orientation='vertical',
            brush=pg.mkBrush(100, 149, 237, 50),  # Полупрозрачный синий
            pen=pg.mkPen('b', width=2),
            movable=False,  # Не разрешать перемещение во время создания
            bounds=None
        )

        plot.addItem(region)

        # Сохраняем регион в список (для последующего управления)
        self.temp_selection_regions.append(region)

        return region

    def clear_selection_on_plot(self, plot_index):
        """Удалить выделение с конкретного графика"""
        if plot_index >= len(self.plots):
            return

        plot = self.plots[plot_index]['plot']

        # Найти и удалить все LinearRegionItem с этого графика
        regions_to_remove = []
        for item in plot.items:
            if isinstance(item, pg.LinearRegionItem):
                regions_to_remove.append(item)

        for region in regions_to_remove:
            plot.removeItem(region)
            if region in self.selection_regions:
                self.selection_regions.remove(region)

        # Очистить сохраненные результаты
        if plot_index in self.selection_results:
            del self.selection_results[plot_index]

        # Обновить info_label если больше нет результатов
        if len(self.selection_results) == 0 and self.selection_mode:
            self.info_label.setText(
                '<b style="color: #3498db;">🎯 РЕЖИМ ВЫБОРКИ АКТИВЕН</b><br>'
                'Перетащите мышью на графике для выбора диапазона.<br>'
                'Нажмите кнопку снова для выхода из режима.'
            )

    def clear_all_selections(self):
        """Удалить все выделения со всех графиков"""
        for i in range(len(self.plots)):
            self.clear_selection_on_plot(i)

        self.selection_regions.clear()
        self.selection_results.clear()
        self.temp_selection_regions.clear()
        self.btn_clear_selection.setEnabled(False)

        # Восстановить сообщение в info_label
        if self.selection_mode:
            self.info_label.setText(
                '<b style="color: #3498db;">🎯 РЕЖИМ ВЫБОРКИ АКТИВЕН</b><br>'
                'Перетащите мышью на графике для выбора диапазона.<br>'
                'Нажмите кнопку снова для выхода из режима.'
            )
        else:
            self.info_label.setText(
                'Наведите курсор на график для отображения значений.'
            )


    def format_selection_results(self, gas_type, x_start, x_end, averages, comparisons, plot_data):
        """Форматировать результаты выборки для отображения в info_label"""
        lines = []

        # Заголовок
        lines.append("<b style='font-size: 14px; color: #2980b9;'>📊 РЕЗУЛЬТАТЫ ВЫБОРКИ</b>")
        lines.append(f"<b>Газ:</b> {gas_type}")

        # Временной диапазон
        time_data = plot_data.get('time_data')
        if time_data is not None:
            try:
                start_dt = pd.Timestamp(x_start, unit='s')
                end_dt = pd.Timestamp(x_end, unit='s')
                start_str = start_dt.strftime('%d.%m.%Y %H:%M:%S')
                end_str = end_dt.strftime('%d.%m.%Y %H:%M:%S')
            except:
                start_str = f"{x_start:.2f}"
                end_str = f"{x_end:.2f}"
        else:
            start_str = f"Индекс {int(x_start)}"
            end_str = f"Индекс {int(x_end)}"

        lines.append(f"<b>📅 Период:</b> {start_str} → {end_str}")
        lines.append("")

        # Средние значения
        lines.append("<b style='color: #27ae60;'>Средние значения:</b>")
        for col, stats in averages.items():
            lines.append(
                f"  • <b>{col}:</b> {stats['mean']:.4f} мг/м³ "
                f"<span style='color: #7f8c8d; font-size: 10px;'>"
                f"(n={stats['count']})</span>"
            )

        # Сравнения
        if len(comparisons) > 0:
            lines.append("")
            lines.append("<b style='color: #e74c3c;'>Сравнение пар анализаторов:</b>")

            for comp in comparisons:
                col1, col2 = comp['pair']
                diff_abs = comp['diff_abs']
                diff_pct = comp['diff_pct']
                correlation = comp.get('correlation', np.nan)

                # Цвет в зависимости от величины разницы
                if pd.isna(diff_pct):
                    color = '#95a5a6'
                    pct_str = 'N/A'
                elif abs(diff_pct) > 10:
                    color = '#e74c3c'  # Красный
                    pct_str = f"{diff_pct:+.2f}%"
                elif abs(diff_pct) > 5:
                    color = '#f39c12'  # Оранжевый
                    pct_str = f"{diff_pct:+.2f}%"
                else:
                    color = '#27ae60'  # Зеленый
                    pct_str = f"{diff_pct:+.2f}%"

                # Форматирование коэффициента корреляции
                if pd.notna(correlation):
                    corr_str = f"r={correlation:.4f}"
                else:
                    corr_str = "r=N/A"

                # Форматирование приведенной погрешности
                reduced_error = comp.get('reduced_error')
                error_str = ""
                if reduced_error is not None:
                    error_str = f", <span style='color: #9C27B0;'>γ={reduced_error:.2f}%</span>"

                lines.append(
                    f"  • <b>{col2}</b> vs <b>{col1}:</b> "
                    f"<span style='color: {color};'>{diff_abs:+.4f} мг/м³ ({pct_str})</span>, "
                    f"<span style='color: #3498db;'>{corr_str}</span>"
                    f"{error_str}"
                )

        return '<br>'.join(lines)

    def format_all_selection_results(self, x_start, x_end, results_by_plot):
        """Форматировать результаты выборки для всех графиков в две колонки"""

        # Временной диапазон (общий для всех)
        if results_by_plot and results_by_plot[0]['plot_data'].get('time_data') is not None:
            try:
                start_dt = pd.Timestamp(x_start, unit='s')
                end_dt = pd.Timestamp(x_end, unit='s')
                start_str = start_dt.strftime('%d.%m.%Y %H:%M:%S')
                end_str = end_dt.strftime('%d.%m.%Y %H:%M:%S')
            except:
                start_str = f"{x_start:.2f}"
                end_str = f"{x_end:.2f}"
        else:
            start_str = f"Индекс {int(x_start)}"
            end_str = f"Индекс {int(x_end)}"

        # Начинаем HTML таблицу
        html = f"""
        <div style='font-size: 11px;'>
            <div style='text-align: center; margin-bottom: 5px;'>
                <b style='font-size: 12px; color: #2980b9;'>📊 РЕЗУЛЬТАТЫ ВЫБОРКИ ДЛЯ ВСЕХ ГРАФИКОВ</b><br>
                <b>Период:</b> {start_str} → {end_str}
            </div>
            <table width='100%' cellspacing='0' cellpadding='3' style='border-collapse: collapse;'>
                <tr>
        """

        # Создаём колонки для каждого графика
        for result in results_by_plot:
            gas_type = result['gas_type']
            averages = result['averages']
            comparisons = result['comparisons']

            # Начало колонки
            html += f"""
                    <td width='50%' valign='top' style='padding: 3px; border: 1px solid #d0d0d0;'>
                        <b style='color: #2c3e50; font-size: 12px;'>▶ {gas_type}</b><br>
                        <b style='color: #27ae60; font-size: 10px;'>Средние значения:</b><br>
            """

            # Средние значения
            for col, stats in averages.items():
                html += f"""
                        <span style='font-size: 10px;'>• <b>{col}:</b> {stats['mean']:.4f} мг/м³
                        <span style='color: #7f8c8d; font-size: 9px;'>(n={stats['count']})</span></span><br>
                """

            # Сравнения
            if len(comparisons) > 0:
                html += """
                        <b style='color: #e74c3c; font-size: 10px;'>Сравнение пар анализаторов:</b><br>
                """

                for comp in comparisons:
                    col1, col2 = comp['pair']
                    diff_abs = comp['diff_abs']
                    diff_pct = comp['diff_pct']
                    correlation = comp.get('correlation', np.nan)

                    # Цвет в зависимости от величины разницы
                    if pd.isna(diff_pct):
                        color = '#95a5a6'
                        pct_str = 'N/A'
                    elif abs(diff_pct) > 10:
                        color = '#e74c3c'  # Красный
                        pct_str = f"{diff_pct:+.2f}%"
                    elif abs(diff_pct) > 5:
                        color = '#f39c12'  # Оранжевый
                        pct_str = f"{diff_pct:+.2f}%"
                    else:
                        color = '#27ae60'  # Зеленый
                        pct_str = f"{diff_pct:+.2f}%"

                    # Форматирование коэффициента корреляции
                    if pd.notna(correlation):
                        corr_str = f"r={correlation:.4f}"
                    else:
                        corr_str = "r=N/A"

                    # Форматирование приведенной погрешности
                    reduced_error = comp.get('reduced_error')
                    error_str = ""
                    if reduced_error is not None:
                        error_str = f", <span style='color: #9C27B0;'>γ={reduced_error:.2f}%</span>"

                    html += f"""
                        <span style='font-size: 10px;'>• <b>{col2}</b> vs <b>{col1}:</b>
                        <span style='color: {color};'>{diff_abs:+.4f} мг/м³ ({pct_str})</span>,
                        <span style='color: #3498db;'>{corr_str}</span>{error_str}</span><br>
                    """

            # Конец колонки
            html += """
                    </td>
            """

        # Закрываем таблицу
        html += """
                </tr>
            </table>
        </div>
        """

        return html

    def process_all_selections(self, x_start, x_end):
        """Обработать выделение для всех графиков одновременно"""
        results_by_plot = []

        for plot_index in range(len(self.plots)):
            plot_data = self.plots[plot_index]
            gas_type = plot_data['gas_type']

            # Извлечь данные в диапазоне
            timestamps = plot_data['timestamps']
            filtered_data = plot_data['filtered_data']
            data_cols = plot_data['data_cols']
            
            extracted_data = {}
            for col in data_cols:
                if col in filtered_data:
                    values = filtered_data[col]
                    extracted = self.logic.extract_range_data(timestamps, values, x_start, x_end)
                    if extracted is not None:
                        extracted_data[col] = extracted

            if not extracted_data or len(extracted_data) == 0:
                continue

            # Рассчитать средние значения
            averages = self.logic.calculate_averages(extracted_data)

            # Рассчитать попарные сравнения с корреляцией и приведенной погрешностью
            comparisons = self.logic.calculate_comparisons(
                averages, extracted_data, self.analyzer_scales, gas_type
            )

            # Сохранить результаты
            self.selection_results[plot_index] = {
                'gas_type': gas_type,
                'range': (x_start, x_end),
                'averages': averages,
                'comparisons': comparisons
            }

            results_by_plot.append({
                'plot_index': plot_index,
                'gas_type': gas_type,
                'averages': averages,
                'comparisons': comparisons,
                'plot_data': plot_data
            })

        # Форматировать и отобразить результаты для всех графиков
        if results_by_plot:
            formatted_text = self.format_all_selection_results(x_start, x_end, results_by_plot)
            self.info_label.setText(formatted_text)

            # Сделать LinearRegionItem перемещаемыми после создания
            for region in self.temp_selection_regions:
                region.setMovable(True)
                self.selection_regions.append(region)

                # Подключить сигнал для автоматического пересчета при изменении
                # Используем lambda с замыканием для передачи всех графиков
                region.sigRegionChanged.connect(self.on_any_selection_region_changed)

            self.temp_selection_regions.clear()

            # Активировать кнопку очистки
            self.btn_clear_selection.setEnabled(True)
        else:
            self.info_label.setText(
                '<span style="color: #e74c3c;">В выбранном диапазоне нет данных.</span>'
            )
            self.clear_all_selections()

    def process_selection(self, plot_index, x_start, x_end):
        """Обработать выделение: извлечь данные, рассчитать и отобразить результаты"""
        plot_data = self.plots[plot_index]
        gas_type = plot_data['gas_type']

        # Извлечь данные в диапазоне
        timestamps = plot_data['timestamps']
        filtered_data = plot_data['filtered_data']
        data_cols = plot_data['data_cols']
        
        extracted_data = {}
        for col in data_cols:
            if col in filtered_data:
                values = filtered_data[col]
                extracted = self.logic.extract_range_data(timestamps, values, x_start, x_end)
                if extracted is not None:
                    extracted_data[col] = extracted

        if not extracted_data or len(extracted_data) == 0:
            self.info_label.setText(
                '<span style="color: #e74c3c;">В выбранном диапазоне нет данных.</span>'
            )
            self.clear_selection_on_plot(plot_index)
            return

        # Рассчитать средние значения
        averages = self.logic.calculate_averages(extracted_data)

        # Рассчитать попарные сравнения с корреляцией и приведенной погрешностью
        comparisons = self.logic.calculate_comparisons(
            averages, extracted_data, self.analyzer_scales, gas_type
        )

        # Форматировать и отобразить результаты
        formatted_text = self.format_selection_results(
            gas_type, x_start, x_end, averages, comparisons, plot_data
        )
        self.info_label.setText(formatted_text)

        # Сохранить результаты
        self.selection_results[plot_index] = {
            'gas_type': gas_type,
            'range': (x_start, x_end),
            'averages': averages,
            'comparisons': comparisons,
            'formatted_text': formatted_text
        }

        # Сделать LinearRegionItem перемещаемым после создания
        if self.current_selection_region:
            self.current_selection_region.setMovable(True)
            self.selection_regions.append(self.current_selection_region)

            # Подключить сигнал для автоматического пересчета при изменении
            self.current_selection_region.sigRegionChanged.connect(
                lambda: self.on_selection_region_changed(plot_index)
            )

            self.current_selection_region = None

        # Активировать кнопку очистки
        self.btn_clear_selection.setEnabled(True)

    def on_any_selection_region_changed(self):
        """Обработчик изменения любого выделения (пользователь переместил/изменил размер)"""
        # Получаем новые границы из первого региона (все синхронизированы)
        if len(self.selection_regions) == 0:
            return

        first_region = self.selection_regions[0]
        x_start, x_end = first_region.getRegion()

        # Синхронизируем все регионы
        for region in self.selection_regions[1:]:
            region.setRegion([x_start, x_end])

        # Пересчитать для всех графиков с новыми границами
        self.process_all_selections(x_start, x_end)

    def on_selection_region_changed(self, plot_index):
        """Обработчик изменения выделения (пользователь переместил/изменил размер)"""
        if plot_index >= len(self.plots):
            return

        plot = self.plots[plot_index]['plot']

        # Найти LinearRegionItem для этого графика
        region = None
        for item in plot.items:
            if isinstance(item, pg.LinearRegionItem):
                region = item
                break

        if region is None:
            return

        # Получить новые границы
        x_start, x_end = region.getRegion()

        # Пересчитать с новыми границами
        self.process_selection(plot_index, x_start, x_end)

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
