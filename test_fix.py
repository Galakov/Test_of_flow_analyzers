# -*- coding: utf-8 -*-
"""
Тест исправления парсинга дат
"""
import pandas as pd

file_path = r"C:\2. Areas\Работа\Soft\Истытания ЭкоСпектр на ОГПЗ\СВОД H2S (01.09-24.11).xlsx"
df = pd.read_excel(file_path)

time_col = 'DateTime'

print("="*80)
print("ТЕСТ ИСПРАВЛЕННОГО ПАРСИНГА")
print("="*80)

# Эмулируем логику из analyzer_comparison.py
parsed = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')
initial_invalid = parsed.isna().sum()
print(f"\nПосле первичного парсинга:")
print(f"  Успешно: {parsed.notna().sum()} ({parsed.notna().sum()/len(df)*100:.1f}%)")
print(f"  Не распарсено: {initial_invalid} ({initial_invalid/len(df)*100:.1f}%)")

if parsed.isna().any():
    print(f"\nПробуем дополнительные форматы...")

    formats_to_try = [
        '%d.%m.%Y %H:%M',         # формат без секунд
        '%d.%m.%Y %H:%M:%S',
    ]

    for fmt in formats_to_try:
        current_invalid = parsed.isna()
        if not current_invalid.any():
            break

        current_invalid_values = df.loc[current_invalid, time_col]
        try:
            parsed_manual = pd.to_datetime(current_invalid_values, format=fmt, errors='coerce')
            success_mask = parsed_manual.notna()
            if success_mask.any():
                success_indices = current_invalid_values.index[success_mask]
                parsed.loc[success_indices] = parsed_manual[success_mask]
                print(f"  Восстановлено {success_mask.sum()} записей с форматом '{fmt}'")
        except Exception as e:
            print(f"  Ошибка с форматом '{fmt}': {e}")

final_invalid = parsed.isna().sum()
print(f"\nПосле дополнительных форматов:")
print(f"  Успешно: {parsed.notna().sum()} ({parsed.notna().sum()/len(df)*100:.1f}%)")
print(f"  Не распарсено: {final_invalid} ({final_invalid/len(df)*100:.1f}%)")

if parsed.notna().any():
    print(f"\nДиапазон дат:")
    print(f"  От: {parsed.min()}")
    print(f"  До: {parsed.max()}")

    # Проверяем, есть ли дата из скриншота
    target = pd.to_datetime('22.11.2025 16:20:00', dayfirst=True)
    before_target = (parsed <= target).sum()
    after_target = (parsed > target).sum()
    print(f"\nПроверка целевой даты ({target}):")
    print(f"  Дат до/включая: {before_target}")
    print(f"  Дат после: {after_target}")

    # Ищем ближайшую
    time_diff = abs(parsed - target)
    if time_diff.notna().any():
        closest_idx = time_diff.idxmin()
        print(f"\n  Ближайшая дата:")
        print(f"    Индекс: {closest_idx}")
        print(f"    Дата: {parsed.iloc[closest_idx]}")
        print(f"    Исходная: {df[time_col].iloc[closest_idx]}")
        print(f"    Ametek: {df['Ametek'].iloc[closest_idx]}")
        print(f"    ЭкоСпектр: {df['ЭкоСпектр'].iloc[closest_idx]}")

print("\n" + "="*80)
print("РЕЗУЛЬТАТ")
print("="*80)

if final_invalid == 0:
    print("\n✓ ВСЕ ДАТЫ УСПЕШНО РАСПАРСЕНЫ!")
else:
    print(f"\n⚠ Осталось {final_invalid} нераспарсенных дат")
    if final_invalid > 0:
        print("\nПримеры нераспарсенных:")
        for idx in df[parsed.isna()].index[:5]:
            print(f"  Строка {idx}: '{df[time_col].iloc[idx]}'")
