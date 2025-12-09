# Искать все файлы (по умолчанию)
python file_encoding_finder.py /path/to/dir

# Искать только файлы без расширения
python file_encoding_finder.py /path/to/dir -e .

# Искать файлы с расширением .txt и без расширения
python file_encoding_finder.py /path/to/dir -e .txt .

# Искать файлы с расширением .txt или .csv (можно без точки)
python file_encoding_finder.py /path/to/dir -e txt csv

# Искать файлы с любым расширением .py
python file_encoding_finder.py /path/to/dir -e .py

# Комбинированный пример
python file_encoding_finder.py /path/to/dir -e .txt .py . -c utf8 win1251 -x node_modules --verbose