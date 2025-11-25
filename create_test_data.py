# -*- coding: utf-8 -*-
"""
Скрипт для создания тестовых данных
Используется для проверки работы программы
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_data():
    """Создание тестовых файлов Excel с данными анализаторов"""
    
    # Генерация временного ряда (2 недели с интервалом 1 час)
    start_date = datetime(2024, 10, 13, 0, 0, 0)
    time_points = [start_date + timedelta(hours=i) for i in range(360)]
    
    # === Создание файла H2S ===
    print("Создание тестового файла H2S...")
    
    # Генерация данных H2S (с небольшим шумом и трендом)
    base_h2s_1 = 5.0  # Базовая концентрация первого анализатора
    base_h2s_2 = 5.2  # Базовая концентрация второго анализатора
    
    h2s_analyzer_1 = base_h2s_1 + np.random.normal(0, 0.5, len(time_points)) + \
                     0.5 * np.sin(np.linspace(0, 4*np.pi, len(time_points)))
    
    h2s_analyzer_2 = base_h2s_2 + np.random.normal(0, 0.6, len(time_points)) + \
                     0.5 * np.sin(np.linspace(0, 4*np.pi, len(time_points)))
    
    # Создание DataFrame для H2S
    df_h2s = pd.DataFrame({
        'Дата и время': time_points,
        'H2S Анализатор 1 (мг/м³)': np.round(h2s_analyzer_1, 4),
        'H2S Анализатор 2 (мг/м³)': np.round(h2s_analyzer_2, 4),
        'Разница (мг/м³)': np.round(h2s_analyzer_2 - h2s_analyzer_1, 4)
    })
    
    # Сохранение в Excel
    df_h2s.to_excel('test_H2S_data.xlsx', index=False)
    print(f"✓ Создан файл: test_H2S_data.xlsx ({len(df_h2s)} записей)")
    
    # === Создание файла SO2 ===
    print("Создание тестового файла SO2...")
    
    # Генерация данных SO2
    base_so2_1 = 10.0  # Базовая концентрация первого анализатора
    base_so2_2 = 10.3  # Базовая концентрация второго анализатора
    
    so2_analyzer_1 = base_so2_1 + np.random.normal(0, 0.8, len(time_points)) + \
                     1.0 * np.sin(np.linspace(0, 6*np.pi, len(time_points)))
    
    so2_analyzer_2 = base_so2_2 + np.random.normal(0, 0.9, len(time_points)) + \
                     1.0 * np.sin(np.linspace(0, 6*np.pi, len(time_points)))
    
    # Создание DataFrame для SO2
    df_so2 = pd.DataFrame({
        'Дата и время': time_points,
        'SO2 Анализатор 1 (мг/м³)': np.round(so2_analyzer_1, 4),
        'SO2 Анализатор 2 (мг/м³)': np.round(so2_analyzer_2, 4),
        'Разница (мг/м³)': np.round(so2_analyzer_2 - so2_analyzer_1, 4)
    })
    
    # Сохранение в Excel
    df_so2.to_excel('test_SO2_data.xlsx', index=False)
    print(f"✓ Создан файл: test_SO2_data.xlsx ({len(df_so2)} записей)")
    
    print("\n" + "="*50)
    print("Тестовые файлы успешно созданы!")
    print("="*50)
    print("\nИспользуйте эти файлы для тестирования программы:")
    print("  - test_H2S_data.xlsx")
    print("  - test_SO2_data.xlsx")
    print("\nЗапустите analyzer_comparison.py и загрузите эти файлы.")


if __name__ == '__main__':
    create_test_data()

