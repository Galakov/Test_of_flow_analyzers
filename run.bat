@echo off
chcp 65001 >nul
echo ========================================
echo   ЗАПУСК ПРОГРАММЫ СРАВНЕНИЯ АНАЛИЗАТОРОВ
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.7 или выше
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python найден
echo.

REM Проверка наличия основного файла
if not exist "analyzer_comparison.py" (
    echo [ОШИБКА] Файл analyzer_comparison.py не найден!
    echo Убедитесь, что вы находитесь в правильной папке
    pause
    exit /b 1
)

echo [INFO] Основной файл найден
echo.

REM Установка зависимостей (если requirements.txt существует)
if exist "requirements.txt" (
    echo [INFO] Установка зависимостей...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARNING] Не удалось установить некоторые зависимости
        echo Попробуйте установить вручную: pip install pandas numpy PyQt5 pyqtgraph openpyxl
        echo.
    ) else (
        echo [OK] Зависимости установлены
        echo.
    )
)

echo [INFO] Запуск программы...
echo.
echo ========================================
echo.

REM Запуск программы
python analyzer_comparison.py

echo.
echo ========================================
echo [INFO] Программа завершена
pause