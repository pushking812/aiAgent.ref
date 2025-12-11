@echo off
for %%I in ("%CD%") do py %%~nxI.py 

python relationship_analyzer.py /path/to/project -t