# -*- coding: utf-8 -*-
"""
Проверка нулей вокруг целевой даты
"""
import pandas as pd

file_path = r"C:\2. Areas\Работа\Soft\Истытания ЭкоСпектр на ОГПЗ\СВОД H2S (01.09-24.11).xlsx"
df = pd.read_excel(file_path)

print("="*80)
print("ПРОВЕРКА ДАННЫХ ВОКРУГ 22.11.2025 16:20")
print("="*80)

# Находим строки вокруг целевой даты
target_idx = 11907  # Из предыдущего теста

print(f"\nДанные за несколько часов вокруг строки {target_idx}:")
print("="*80)

# Показываем 20 строк до и 20 после
start_idx = max(0, target_idx - 20)
end_idx = min(len(df), target_idx + 21)

print(f"\nDateTime                 | Ametek | ЭкоСпектр")
print("-" * 60)

for idx in range(start_idx, end_idx):
    dt = df['DateTime'].iloc[idx]
    ametek = df['Ametek'].iloc[idx]
    eco = df['ЭкоСпектр'].iloc[idx]

    # Отмечаем целевую строку
    marker = " <-- ЦЕЛЕВАЯ" if idx == target_idx else ""

    # Отмечаем нули в ЭкоСпектр
    eco_marker = ""
    if eco == 0 or eco == '0':
        eco_marker = " [НОЛЬ!]"

    print(f"{dt:25} | {str(ametek):6} | {str(eco):9}{eco_marker}{marker}")

print("\n" + "="*80)
print("СТАТИСТИКА НУЛЕЙ")
print("="*80)

# Считаем нули в разных диапазонах
eco_numeric = pd.to_numeric(df['ЭкоСпектр'], errors='coerce')
ametek_numeric = pd.to_numeric(df['Ametek'], errors='coerce')

# В целом файле
total_eco_zeros = (eco_numeric == 0).sum()
total_ametek_zeros = (ametek_numeric == 0).sum()

print(f"\nВо всем файле:")
print(f"  ЭкоСпектр: {total_eco_zeros} нулей из {len(df)} ({total_eco_zeros/len(df)*100:.1f}%)")
print(f"  Ametek: {total_ametek_zeros} нулей из {len(df)} ({total_ametek_zeros/len(df)*100:.1f}%)")

# В районе целевой даты (±100 строк)
window_start = max(0, target_idx - 100)
window_end = min(len(df), target_idx + 100)

window_eco = eco_numeric[window_start:window_end]
window_ametek = ametek_numeric[window_start:window_end]

window_eco_zeros = (window_eco == 0).sum()
window_ametek_zeros = (window_ametek == 0).sum()

print(f"\nВ окне ±100 записей от целевой даты:")
print(f"  ЭкоСпектр: {window_eco_zeros} нулей из {len(window_eco)} ({window_eco_zeros/len(window_eco)*100:.1f}%)")
print(f"  Ametek: {window_ametek_zeros} нулей из {len(window_ametek)} ({window_ametek_zeros/len(window_ametek)*100:.1f}%)")

# Проверка на текстовые нули
print(f"\n" + "="*80)
print("ПРОВЕРКА НА ТЕКСТОВЫЕ НУЛИ VS ЧИСЛОВЫЕ")
print("="*80)

# Проверяем тип данных в строке с нулем
target_eco_value = df['ЭкоСпектр'].iloc[target_idx]
print(f"\nЗначение ЭкоСпектр в целевой строке:")
print(f"  Значение: '{target_eco_value}'")
print(f"  Тип: {type(target_eco_value)}")
print(f"  Repr: {repr(target_eco_value)}")

# Проверяем несколько строк с нулями
print(f"\nПримеры строк с нулями в ЭкоСпектр:")
zero_indices = df.index[eco_numeric == 0].tolist()[:10]
for idx in zero_indices:
    val = df['ЭкоСпектр'].iloc[idx]
    dt = df['DateTime'].iloc[idx]
    print(f"  Строка {idx} ({dt}): '{val}' (тип: {type(val).__name__})")
