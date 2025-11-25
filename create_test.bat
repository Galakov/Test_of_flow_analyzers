@echo off
chcp 65001 >nul
echo Создание тестовых данных...
python create_test_data.py
echo.
echo Готово!
pause

