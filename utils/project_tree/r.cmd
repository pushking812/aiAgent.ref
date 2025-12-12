@echo off
for %%I in ("%CD%") do py %%~nxI.py ..\..\ --exclude "tests,utils" %1