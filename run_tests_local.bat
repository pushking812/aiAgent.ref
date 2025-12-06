@echo off
REM run_tests_local.bat - Для Windows

echo 🚀 Запуск тестов на Windows...
echo ============================================================

REM Создаем виртуальное окружение
if not exist venv (
    echo Создание виртуального окружения...
    python -m venv venv
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo Установка зависимостей...
pip install --upgrade pip
pip install -r requirements-test.txt

REM Запускаем тесты
echo Запуск тестов...
python run_tests.py

pause