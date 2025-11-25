@echo off
chcp 65001 >nul
echo ========================================
echo   СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.7 или выше
    pause
    exit /b 1
)

echo [INFO] Python найден
echo.

REM Проверка наличия файла создания тестов
if not exist "create_test_data.py" (
    echo [ОШИБКА] Файл create_test_data.py не найден!
    pause
    exit /b 1
)

echo [INFO] Файл генератора найден
echo.

REM Установка зависимостей pandas и openpyxl (если нужно)
echo [INFO] Проверка зависимостей...
python -c "import pandas, numpy, openpyxl" 2>nul
if errorlevel 1 (
    echo [INFO] Установка необходимых библиотек...
    python -m pip install pandas numpy openpyxl
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить зависимости
        echo Установите вручную: pip install pandas numpy openpyxl
        pause
        exit /b 1
    )
)

echo [OK] Зависимости готовы
echo.

echo [INFO] Создание тестовых файлов...
echo.
echo ========================================
echo.

REM Запуск создания тестовых данных
python create_test_data.py

echo.
echo ========================================
echo [INFO] Готово! Тестовые файлы созданы.
echo.
echo Теперь можете запустить программу:
echo   run.bat
echo.
echo И загрузить созданные файлы:
echo   - test_H2S_data.xlsx
echo   - test_SO2_data.xlsx
echo.
pause