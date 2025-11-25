# -*- coding: utf-8 -*-
"""
Скрипт для отладки данных из Excel файла
"""
import pandas as pd
import numpy as np

# Читаем файл
file_path = r"C:\2. Areas\Работа\Soft\Истытания ЭкоСпектр на ОГПЗ\СВОД H2S (01.09-24.11).xlsx"
df = pd.read_excel(file_path)

print("=" * 80)
print("СТРУКТУРА ФАЙЛА")
print("=" * 80)
print(f"\nВсего строк: {len(df)}")
print(f"Колонки: {list(df.columns)}")
print(f"\nТипы данных:")
print(df.dtypes)

print("\n" + "=" * 80)
print("ПЕРВЫЕ 20 СТРОК")
print("=" * 80)
print(df.head(20).to_string())

print("\n" + "=" * 80)
print("СТРОКИ С ПРОБЛЕМНОЙ ДАТОЙ (22.11.2025 16:20:00)")
print("=" * 80)

# Ищем строки с этой датой
time_col = df.columns[0]  # Предполагаем, что первая колонка - время
target_date = pd.to_datetime('22.11.2025 16:20:00', dayfirst=True)

# Пробуем распарсить время
parsed_time = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')
df['_parsed_time'] = parsed_time

# Ищем строки около целевой даты
mask = (parsed_time >= target_date - pd.Timedelta(minutes=30)) & \
       (parsed_time <= target_date + pd.Timedelta(minutes=30))

if mask.any():
    print(f"\nНайдено {mask.sum()} строк около целевой даты:")
    print(df[mask].to_string())
else:
    print("\nСтроки около целевой даты не найдены")
    print(f"Ближайшая дата к {target_date}:")
    time_diff = abs(parsed_time - target_date)
    if time_diff.notna().any():
        closest_idx = time_diff.idxmin()
        print(df.loc[[closest_idx]].to_string())
    else:
        print("Не удалось распарсить даты из файла")

print("\n" + "=" * 80)
print("АНАЛИЗ ЗНАЧЕНИЙ В КОЛОНКАХ ДАННЫХ")
print("=" * 80)

# Исключаем первую колонку (время) и анализируем остальные
for col in df.columns[1:]:
    print(f"\n--- Колонка: {col} ---")
    print(f"Тип данных: {df[col].dtype}")

    # Проверяем, есть ли строковые значения
    sample_values = df[col].head(10)
    print("Первые 10 значений:")
    for i, val in enumerate(sample_values):
        print(f"  [{i}] '{val}' (тип: {type(val).__name__})")

    # Пробуем преобразовать в числа
    numeric_values = pd.to_numeric(df[col], errors='coerce')

    valid_count = numeric_values.notna().sum()
    invalid_count = numeric_values.isna().sum()
    zero_count = (numeric_values == 0).sum()
    non_zero_count = ((numeric_values != 0) & numeric_values.notna()).sum()

    print(f"Статистика преобразования pd.to_numeric:")
    print(f"  Валидных: {valid_count}, Невалидных: {invalid_count}")
    print(f"  Нулей: {zero_count}, Ненулевых: {non_zero_count}")

    if non_zero_count > 0:
        print(f"  Диапазон ненулевых: {numeric_values[numeric_values != 0].min():.4f} - {numeric_values[numeric_values != 0].max():.4f}")

    # Проверяем случаи, где значение стало нулем
    became_zero = (numeric_values == 0) & (df[col] != 0) & (df[col] != '0') & df[col].notna()
    if became_zero.any():
        print(f"  ⚠ ПРОБЛЕМА: {became_zero.sum()} значений стали нулями после pd.to_numeric!")
        problem_samples = df[col][became_zero].head(5)
        for idx, val in problem_samples.items():
            print(f"    Строка {idx}: '{val}' -> 0")

print("\n" + "=" * 80)
print("ПРОВЕРКА НА ЗАПЯТЫЕ В ЧИСЛАХ")
print("=" * 80)

for col in df.columns[1:]:
    # Проверяем, есть ли строковые значения с запятыми
    string_mask = df[col].astype(str).str.contains(',', na=False)
    if string_mask.any():
        print(f"\n{col}: найдено {string_mask.sum()} значений с запятыми")
        samples = df[col][string_mask].head(5)
        for idx, val in samples.items():
            print(f"  Строка {idx}: '{val}'")
