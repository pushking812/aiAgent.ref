Примеры использования:
    Простой поиск с выводом по умолчанию (путь: кодировка):
python file_encoding_finder.py /path/to/directory
    Поиск с конкретными расширениями:
python file_encoding_finder.py /path/to/directory --extensions .txt .csv
    Подробный вывод:
python file_encoding_finder.py /path/to/directory --verbose
    Сохранить в файл:
python file_encoding_finder.py /path/to/directory --output results
    Только путь и кодировка (quiet режим):
python file_encoding_finder.py /path/to/directory --quiet
    С ограничением вывода:
python file_encoding_finder.py /path/to/directory --limit 10
    Комбинированные параметры:
python file_encoding_finder.py /path/to/directory --extensions .txt .py --encodings utf8 --verbose --output results.json --format json

Пример вывода по умолчанию:

/home/user/documents/file1.txt: utf-8
/home/user/documents/file2.txt: windows-1251
/home/user/documents/subdir/file3.csv: utf-8

Пример подробного вывода (с --verbose):

Поиск файлов в: /home/user/documents
Расширения: ['.txt', '.csv']
Кодировки: ['utf8', 'win1251']

============================================================
Найдено файлов: 3
============================================================
1. /home/user/documents/file1.txt
   Кодировка: utf-8
   Размер: 1024 байт
   Расширение: .txt
   Директория: /home/user/documents
2. /home/user/documents/file2.txt
   Кодировка: windows-1251
   Размер: 2048 байт
   Расширение: .txt
   Директория: /home/user/documents
3. /home/user/documents/subdir/file3.csv
   Кодировка: utf-8
   Размер: 512 байт
   Расширение: .csv
   Директория: /home/user/documents/subdir