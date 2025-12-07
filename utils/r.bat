@echo off
if not "%~1"=="" (
    notepad++ %CD%\%1 -n%2 
) else (
    echo ""
)


