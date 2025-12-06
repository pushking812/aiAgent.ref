@echo off
:: Рекурсивная очистка кэша pytest и Python
echo Очистка кэша Python/pytest...

:: Рекурсивное удаление папок .pytest_cache
if exist .pytest_cache rd /s /q .pytest_cache
for /d /r %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"

:: Рекурсивное удаление папок __pycache__
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: Рекурсивное удаление папок coverage_html
if exist coverage_html rd /s /q coverage_html
for /d /r %%d in (coverage_html) do @if exist "%%d" rd /s /q "%%d"

:: Удаление файлов .coverage в текущей и подкаталогах
del /s /q .coverage 2>nul
del /s /q .coverage.* 2>nul

:: Дополнительная очистка
if exist htmlcov rd /s /q htmlcov
if exist .mypy_cache rd /s /q .mypy_cache
if exist .tox rd /s /q .tox
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.egg-info rd /s /q *.egg-info 2>nul

echo Очистка завершена!
pause