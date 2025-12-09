@echo off
set TARGET_DIR=%1

rem Создаем папку если не существует
if not exist %1 (
    echo Создаю папку %1...
    mkdir %1
)

rem Перемещаем файлы начинающиеся на dep
for %%f in (%1*) do (
    if exist %%f (
        echo Перемещаю: %%f
        move %%f %1
    )
)

echo Готово!
pause