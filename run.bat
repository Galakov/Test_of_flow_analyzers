@echo off
chcp 65001 >nul
echo Запуск программы сравнения анализаторов...
echo.

REM Проверка установленных зависимостей
python -c "import PyQt5, pandas, pyqtgraph" 2>nul
if errorlevel 1 (
    echo Установка зависимостей...
    pip install -r requirements.txt
    echo.
)

REM Запуск программы
python analyzer_comparison.py

pause

