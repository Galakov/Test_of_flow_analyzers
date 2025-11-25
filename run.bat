@echo off
chcp 65001 >nul
echo ========================================
echo   Р—РђРџРЈРЎРљ РџР РћР“Р РђРњРњР« РЎР РђР’РќР•РќРРЇ РђРќРђР›РР—РђРўРћР РћР’
echo ========================================
echo.

REM РџСЂРѕРІРµСЂРєР° РЅР°Р»РёС‡РёСЏ Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [РћРЁРР‘РљРђ] Python РЅРµ РЅР°Р№РґРµРЅ!
    echo РЈСЃС‚Р°РЅРѕРІРёС‚Рµ Python 3.7 РёР»Рё РІС‹С€Рµ
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python РЅР°Р№РґРµРЅ
echo.

REM РџСЂРѕРІРµСЂРєР° РЅР°Р»РёС‡РёСЏ РѕСЃРЅРѕРІРЅРѕРіРѕ С„Р°Р№Р»Р°
if not exist "analyzer_comparison.py" (
    echo [РћРЁРР‘РљРђ] Р¤Р°Р№Р» analyzer_comparison.py РЅРµ РЅР°Р№РґРµРЅ!
    echo РЈР±РµРґРёС‚РµСЃСЊ, С‡С‚Рѕ РІС‹ РЅР°С…РѕРґРёС‚РµСЃСЊ РІ РїСЂР°РІРёР»СЊРЅРѕР№ РїР°РїРєРµ
    pause
    exit /b 1
)

echo [INFO] РћСЃРЅРѕРІРЅРѕР№ С„Р°Р№Р» РЅР°Р№РґРµРЅ
echo.

REM РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№ (РµСЃР»Рё requirements.txt СЃСѓС‰РµСЃС‚РІСѓРµС‚)
if exist "requirements.txt" (
    echo [INFO] РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARNING] РќРµ СѓРґР°Р»РѕСЃСЊ СѓСЃС‚Р°РЅРѕРІРёС‚СЊ РЅРµРєРѕС‚РѕСЂС‹Рµ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё
        echo РџРѕРїСЂРѕР±СѓР№С‚Рµ СѓСЃС‚Р°РЅРѕРІРёС‚СЊ РІСЂСѓС‡РЅСѓСЋ: pip install pandas numpy PyQt5 pyqtgraph openpyxl
        echo.
    ) else (
        echo [OK] Р—Р°РІРёСЃРёРјРѕСЃС‚Рё СѓСЃС‚Р°РЅРѕРІР»РµРЅС‹
        echo.
    )
)

echo [INFO] Р—Р°РїСѓСЃРє РїСЂРѕРіСЂР°РјРјС‹...
echo.
echo ========================================
echo.

REM Р—Р°РїСѓСЃРє РїСЂРѕРіСЂР°РјРјС‹
python analyzer_comparison.py

echo.
echo ========================================
echo [INFO] РџСЂРѕРіСЂР°РјРјР° Р·Р°РІРµСЂС€РµРЅР°
pause
