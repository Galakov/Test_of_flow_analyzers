@echo off
chcp 65001 >nul
echo ========================================
echo   РЎРћР—Р”РђРќРР• РўР•РЎРўРћР’Р«РҐ Р”РђРќРќР«РҐ
echo ========================================
echo.

REM РџСЂРѕРІРµСЂРєР° РЅР°Р»РёС‡РёСЏ Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [РћРЁРР‘РљРђ] Python РЅРµ РЅР°Р№РґРµРЅ!
    echo РЈСЃС‚Р°РЅРѕРІРёС‚Рµ Python 3.7 РёР»Рё РІС‹С€Рµ
    pause
    exit /b 1
)

echo [INFO] Python РЅР°Р№РґРµРЅ
echo.

REM РџСЂРѕРІРµСЂРєР° РЅР°Р»РёС‡РёСЏ С„Р°Р№Р»Р° СЃРѕР·РґР°РЅРёСЏ С‚РµСЃС‚РѕРІ
if not exist "create_test_data.py" (
    echo [РћРЁРР‘РљРђ] Р¤Р°Р№Р» create_test_data.py РЅРµ РЅР°Р№РґРµРЅ!
    pause
    exit /b 1
)

echo [INFO] Р¤Р°Р№Р» РіРµРЅРµСЂР°С‚РѕСЂР° РЅР°Р№РґРµРЅ
echo.

REM РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№ pandas Рё openpyxl (РµСЃР»Рё РЅСѓР¶РЅРѕ)
echo [INFO] РџСЂРѕРІРµСЂРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№...
python -c "import pandas, numpy, openpyxl" 2>nul
if errorlevel 1 (
    echo [INFO] РЈСЃС‚Р°РЅРѕРІРєР° РЅРµРѕР±С…РѕРґРёРјС‹С… Р±РёР±Р»РёРѕС‚РµРє...
    python -m pip install pandas numpy openpyxl
    if errorlevel 1 (
        echo [РћРЁРР‘РљРђ] РќРµ СѓРґР°Р»РѕСЃСЊ СѓСЃС‚Р°РЅРѕРІРёС‚СЊ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё
        echo РЈСЃС‚Р°РЅРѕРІРёС‚Рµ РІСЂСѓС‡РЅСѓСЋ: pip install pandas numpy openpyxl
        pause
        exit /b 1
    )
)

echo [OK] Р—Р°РІРёСЃРёРјРѕСЃС‚Рё РіРѕС‚РѕРІС‹
echo.

echo [INFO] РЎРѕР·РґР°РЅРёРµ С‚РµСЃС‚РѕРІС‹С… С„Р°Р№Р»РѕРІ...
echo.
echo ========================================
echo.

REM Р—Р°РїСѓСЃРє СЃРѕР·РґР°РЅРёСЏ С‚РµСЃС‚РѕРІС‹С… РґР°РЅРЅС‹С…
python create_test_data.py

echo.
echo ========================================
echo [INFO] Р“РѕС‚РѕРІРѕ! РўРµСЃС‚РѕРІС‹Рµ С„Р°Р№Р»С‹ СЃРѕР·РґР°РЅС‹.
echo.
echo РўРµРїРµСЂСЊ РјРѕР¶РµС‚Рµ Р·Р°РїСѓСЃС‚РёС‚СЊ РїСЂРѕРіСЂР°РјРјСѓ:
echo   run.bat
echo.
echo Р Р·Р°РіСЂСѓР·РёС‚СЊ СЃРѕР·РґР°РЅРЅС‹Рµ С„Р°Р№Р»С‹:
echo   - test_H2S_data.xlsx
echo   - test_SO2_data.xlsx
echo.
pause
