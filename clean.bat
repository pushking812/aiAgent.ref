:: Очистка кэша pytest и Python
rd /s /q .pytest_cache 2>nul
rd /s /q __pycache__ 2>nul
rd /s /q tests\__pycache__ 2>nul
rd /s /q coverage_html 2>nul
rd /s /q .coverage 2>nul