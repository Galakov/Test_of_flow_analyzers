# -*- coding: utf-8 -*-
"""
Тест парсинга дат
"""
import pandas as pd

file_path = r"C:\2. Areas\Работа\Soft\Истытания ЭкоСпектр на ОГПЗ\СВОД H2S (01.09-24.11).xlsx"
df = pd.read_excel(file_path)

print("=" * 80)
print("ТЕСТ ПАРСИНГА ДАТ")
print("=" * 80)

time_col = 'DateTime'
print(f"\nКолонка времени: {time_col}")
print(f"Тип данных: {df[time_col].dtype}")

# Показываем несколько примеров
print("\nПервые 5 значений:")
for i in range(5):
    val = df[time_col].iloc[i]
    print(f"  [{i}] '{val}' | тип: {type(val).__name__} | repr: {repr(val)}")

# Пробуем разные способы парсинга
print("\n" + "=" * 80)
print("ПОПЫТКИ ПАРСИНГА")
print("=" * 80)

test_value = df[time_col].iloc[0]
print(f"\nТестовое значение: '{test_value}'")

# Попытка 1: dayfirst=True
try:
    result = pd.to_datetime(test_value, dayfirst=True)
    print(f"OK dayfirst=True: {result}")
except Exception as e:
    print(f"FAIL dayfirst=True: {e}")

# Попытка 2: dayfirst=False
try:
    result = pd.to_datetime(test_value, dayfirst=False)
    print(f"OK dayfirst=False: {result}")
except Exception as e:
    print(f"FAIL dayfirst=False: {e}")

# Попытка 3: Указание формата
formats = [
    '%d.%m.%Y %H:%M:%S',
    '%d.%m.%Y %-H:%M:%S',  # без ведущего нуля в часах
    '%d.%m.%Y %k:%M:%S',
]

for fmt in formats:
    try:
        result = pd.to_datetime(test_value, format=fmt)
        print(f"OK Формат '{fmt}': {result}")
    except Exception as e:
        print(f"FAIL Формат '{fmt}': {type(e).__name__}")

# Попытка 4: Парсинг всей колонки
print("\n" + "=" * 80)
print("ПАРСИНГ ВСЕЙ КОЛОНКИ")
print("=" * 80)

for method_name, method_kwargs in [
    ("dayfirst=True", {"dayfirst": True}),
    ("dayfirst=False", {"dayfirst": False}),
    ("infer_datetime_format=True", {"infer_datetime_format": True}),
]:
    try:
        parsed = pd.to_datetime(df[time_col], errors='coerce', **method_kwargs)
        valid_count = parsed.notna().sum()
        print(f"{method_name}: {valid_count} / {len(df)} успешно ({valid_count/len(df)*100:.1f}%)")
        if valid_count > 0:
            print(f"  Пример: {parsed[parsed.notna()].iloc[0]}")
    except Exception as e:
        print(f"{method_name}: ОШИБКА - {e}")

# Проверка, не является ли это datetime объектом Excel
print("\n" + "=" * 80)
print("ПРОВЕРКА ТИПА ДАННЫХ")
print("=" * 80)

print(f"\nТип первого значения: {type(df[time_col].iloc[0])}")
print(f"Это datetime? {isinstance(df[time_col].iloc[0], pd.Timestamp)}")
print(f"Это строка? {isinstance(df[time_col].iloc[0], str)}")

# Если это уже datetime, просто используем как есть
if pd.api.types.is_datetime64_any_dtype(df[time_col]):
    print("\nOK Колонка уже содержит datetime объекты!")
    print(f"Диапазон: {df[time_col].min()} - {df[time_col].max()}")
