# -*- coding: utf-8 -*-
"""
Поиск потерянных данных
"""
import pandas as pd
import numpy as np

file_path = r"C:\2. Areas\Работа\Soft\Истытания ЭкоСпектр на ОГПЗ\СВОД H2S (01.09-24.11).xlsx"
df = pd.read_excel(file_path)

print("="*80)
print("АНАЛИЗ ПОТЕРЯННЫХ ДАННЫХ")
print("="*80)

time_col = 'DateTime'

# Парсим даты
parsed = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')

# Находим строки, где дата не распарсилась
failed_mask = parsed.isna()
failed_count = failed_mask.sum()
success_count = (~failed_mask).sum()

print(f"\nУспешно распарсено: {success_count} ({success_count/len(df)*100:.1f}%)")
print(f"Не распарсено: {failed_count} ({failed_count/len(df)*100:.1f}%)")

if failed_count > 0:
    print(f"\nПримеры нераспарсенных дат (первые 20):")
    failed_dates = df[time_col][failed_mask].head(20)
    for idx, val in failed_dates.items():
        # Проверяем, есть ли ненулевые данные в этой строке
        ametek_val = df.loc[idx, 'Ametek']
        ecospektr_val = df.loc[idx, 'ЭкоСпектр']
        print(f"  Строка {idx}: '{val}' | Ametek={ametek_val}, ЭкоСпектр={ecospektr_val}")

    # Статистика по потерянным данным
    print(f"\n" + "="*80)
    print("СТАТИСТИКА ПОТЕРЯННЫХ ДАННЫХ")
    print("="*80)

    failed_data = df[failed_mask]

    # Для Ametek
    ametek_numeric = pd.to_numeric(failed_data['Ametek'], errors='coerce')
    ametek_non_zero = ((ametek_numeric != 0) & ametek_numeric.notna()).sum()
    print(f"\nAmetek:")
    print(f"  Потеряно строк: {len(failed_data)}")
    print(f"  Из них ненулевых: {ametek_non_zero}")
    if ametek_non_zero > 0:
        print(f"  Диапазон потерянных ненулевых: {ametek_numeric[ametek_numeric != 0].min():.4f} - {ametek_numeric[ametek_numeric != 0].max():.4f}")

    # Для ЭкоСпектр
    eco_numeric = pd.to_numeric(failed_data['ЭкоСпектр'], errors='coerce')
    eco_non_zero = ((eco_numeric != 0) & eco_numeric.notna()).sum()
    print(f"\nЭкоСпектр:")
    print(f"  Потеряно строк: {len(failed_data)}")
    print(f"  Из них ненулевых: {eco_non_zero}")
    if eco_non_zero > 0:
        print(f"  Диапазон потерянных ненулевых: {eco_numeric[eco_numeric != 0].min():.4f} - {eco_numeric[eco_numeric != 0].max():.4f}")

print(f"\n" + "="*80)
print("ПРОВЕРКА НА СКРИНШОТЕ: 22.11.2025 16:20:00")
print("="*80)

# Ищем эту дату в успешно распарсенных
target = pd.to_datetime('22.11.2025 16:20:00', dayfirst=True)
mask = (parsed == target)

if mask.any():
    idx = df[mask].index[0]
    print(f"\nНайдена строка {idx}:")
    print(f"  Дата: {df.loc[idx, time_col]}")
    print(f"  Ametek: {df.loc[idx, 'Ametek']}")
    print(f"  ЭкоСпектр: {df.loc[idx, 'ЭкоСпектр']}")
else:
    # Ищем ближайшую
    time_diff = abs(parsed - target)
    if time_diff.notna().any():
        closest_idx = time_diff.idxmin()
        print(f"\nБлижайшая строка {closest_idx}:")
        print(f"  Дата (исходная): {df.loc[closest_idx, time_col]}")
        print(f"  Дата (распарсенная): {parsed.iloc[closest_idx]}")
        print(f"  Ametek: {df.loc[closest_idx, 'Ametek']}")
        print(f"  ЭкоСпектр: {df.loc[closest_idx, 'ЭкоСпектр']}")
        print(f"  Разница во времени: {time_diff.iloc[closest_idx]}")
    else:
        print("Не найдено ни одной распарсенной даты!")
