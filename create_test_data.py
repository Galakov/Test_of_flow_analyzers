# -*- coding: utf-8 -*-
"""
РЎРєСЂРёРїС‚ РґР»СЏ СЃРѕР·РґР°РЅРёСЏ С‚РµСЃС‚РѕРІС‹С… РґР°РЅРЅС‹С…
РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РґР»СЏ РїСЂРѕРІРµСЂРєРё СЂР°Р±РѕС‚С‹ РїСЂРѕРіСЂР°РјРјС‹
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_data():
    """РЎРѕР·РґР°РЅРёРµ С‚РµСЃС‚РѕРІС‹С… С„Р°Р№Р»РѕРІ Excel СЃ РґР°РЅРЅС‹РјРё Р°РЅР°Р»РёР·Р°С‚РѕСЂРѕРІ"""
    
    # Р“РµРЅРµСЂР°С†РёСЏ РІСЂРµРјРµРЅРЅРѕРіРѕ СЂСЏРґР° (2 РЅРµРґРµР»Рё СЃ РёРЅС‚РµСЂРІР°Р»РѕРј 1 С‡Р°СЃ)
    start_date = datetime(2024, 10, 13, 0, 0, 0)
    time_points = [start_date + timedelta(hours=i) for i in range(360)]
    
    # === РЎРѕР·РґР°РЅРёРµ С„Р°Р№Р»Р° H2S ===
    print("РЎРѕР·РґР°РЅРёРµ С‚РµСЃС‚РѕРІРѕРіРѕ С„Р°Р№Р»Р° H2S...")
    
    # Р“РµРЅРµСЂР°С†РёСЏ РґР°РЅРЅС‹С… H2S (СЃ РЅРµР±РѕР»СЊС€РёРј С€СѓРјРѕРј Рё С‚СЂРµРЅРґРѕРј)
    base_h2s_1 = 5.0  # Р‘Р°Р·РѕРІР°СЏ РєРѕРЅС†РµРЅС‚СЂР°С†РёСЏ РїРµСЂРІРѕРіРѕ Р°РЅР°Р»РёР·Р°С‚РѕСЂР°
    base_h2s_2 = 5.2  # Р‘Р°Р·РѕРІР°СЏ РєРѕРЅС†РµРЅС‚СЂР°С†РёСЏ РІС‚РѕСЂРѕРіРѕ Р°РЅР°Р»РёР·Р°С‚РѕСЂР°
    
    h2s_analyzer_1 = base_h2s_1 + np.random.normal(0, 0.5, len(time_points)) + \
                     0.5 * np.sin(np.linspace(0, 4*np.pi, len(time_points)))
    
    h2s_analyzer_2 = base_h2s_2 + np.random.normal(0, 0.6, len(time_points)) + \
                     0.5 * np.sin(np.linspace(0, 4*np.pi, len(time_points)))
    
    # РЎРѕР·РґР°РЅРёРµ DataFrame РґР»СЏ H2S
    df_h2s = pd.DataFrame({
        'Р”Р°С‚Р° Рё РІСЂРµРјСЏ': time_points,
        'H2S РђРЅР°Р»РёР·Р°С‚РѕСЂ 1 (РјРі/РјВі)': np.round(h2s_analyzer_1, 4),
        'H2S РђРЅР°Р»РёР·Р°С‚РѕСЂ 2 (РјРі/РјВі)': np.round(h2s_analyzer_2, 4),
        'Р Р°Р·РЅРёС†Р° (РјРі/РјВі)': np.round(h2s_analyzer_2 - h2s_analyzer_1, 4)
    })
    
    # РЎРѕС…СЂР°РЅРµРЅРёРµ РІ Excel
    df_h2s.to_excel('test_H2S_data.xlsx', index=False)
    print(f"вњ“ РЎРѕР·РґР°РЅ С„Р°Р№Р»: test_H2S_data.xlsx ({len(df_h2s)} Р·Р°РїРёСЃРµР№)")
    
    # === РЎРѕР·РґР°РЅРёРµ С„Р°Р№Р»Р° SO2 ===
    print("РЎРѕР·РґР°РЅРёРµ С‚РµСЃС‚РѕРІРѕРіРѕ С„Р°Р№Р»Р° SO2...")
    
    # Р“РµРЅРµСЂР°С†РёСЏ РґР°РЅРЅС‹С… SO2
    base_so2_1 = 10.0  # Р‘Р°Р·РѕРІР°СЏ РєРѕРЅС†РµРЅС‚СЂР°С†РёСЏ РїРµСЂРІРѕРіРѕ Р°РЅР°Р»РёР·Р°С‚РѕСЂР°
    base_so2_2 = 10.3  # Р‘Р°Р·РѕРІР°СЏ РєРѕРЅС†РµРЅС‚СЂР°С†РёСЏ РІС‚РѕСЂРѕРіРѕ Р°РЅР°Р»РёР·Р°С‚РѕСЂР°
    
    so2_analyzer_1 = base_so2_1 + np.random.normal(0, 0.8, len(time_points)) + \
                     1.0 * np.sin(np.linspace(0, 6*np.pi, len(time_points)))
    
    so2_analyzer_2 = base_so2_2 + np.random.normal(0, 0.9, len(time_points)) + \
                     1.0 * np.sin(np.linspace(0, 6*np.pi, len(time_points)))
    
    # РЎРѕР·РґР°РЅРёРµ DataFrame РґР»СЏ SO2
    df_so2 = pd.DataFrame({
        'Р”Р°С‚Р° Рё РІСЂРµРјСЏ': time_points,
        'SO2 РђРЅР°Р»РёР·Р°С‚РѕСЂ 1 (РјРі/РјВі)': np.round(so2_analyzer_1, 4),
        'SO2 РђРЅР°Р»РёР·Р°С‚РѕСЂ 2 (РјРі/РјВі)': np.round(so2_analyzer_2, 4),
        'Р Р°Р·РЅРёС†Р° (РјРі/РјВі)': np.round(so2_analyzer_2 - so2_analyzer_1, 4)
    })
    
    # РЎРѕС…СЂР°РЅРµРЅРёРµ РІ Excel
    df_so2.to_excel('test_SO2_data.xlsx', index=False)
    print(f"вњ“ РЎРѕР·РґР°РЅ С„Р°Р№Р»: test_SO2_data.xlsx ({len(df_so2)} Р·Р°РїРёСЃРµР№)")
    
    print("\n" + "="*50)
    print("РўРµСЃС‚РѕРІС‹Рµ С„Р°Р№Р»С‹ СѓСЃРїРµС€РЅРѕ СЃРѕР·РґР°РЅС‹!")
    print("="*50)
    print("\nРСЃРїРѕР»СЊР·СѓР№С‚Рµ СЌС‚Рё С„Р°Р№Р»С‹ РґР»СЏ С‚РµСЃС‚РёСЂРѕРІР°РЅРёСЏ РїСЂРѕРіСЂР°РјРјС‹:")
    print("  - test_H2S_data.xlsx")
    print("  - test_SO2_data.xlsx")
    print("\nР—Р°РїСѓСЃС‚РёС‚Рµ analyzer_comparison.py Рё Р·Р°РіСЂСѓР·РёС‚Рµ СЌС‚Рё С„Р°Р№Р»С‹.")


if __name__ == '__main__':
    create_test_data()
