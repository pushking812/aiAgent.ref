#!/usr/bin/env python3
"""
Модуль для рекурсивного поиска файлов с заданными кодировками.
Поддерживает кодировки: utf8, win1251, macintosh и другие.
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
import csv

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

@dataclass
class FileInfo:
    """Информация о найденном файле"""
    path: str
    encoding: str
    size: int
    extension: str
    directory: str
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return asdict(self)

class FileEncodingFinder:
    """Класс для поиска файлов по кодировкам"""
    
    # Карта алиасов кодировок для нормализации
    ENCODING_ALIASES = {
        # UTF-8
        'utf8': 'utf-8',
        'utf-8': 'utf-8',
        'utf_8': 'utf-8',
        
        # Windows-1251
        'win1251': 'windows-1251',
        'windows-1251': 'windows-1251',
        'cp1251': 'windows-1251',
        '1251': 'windows-1251',
        
        # Macintosh
        'macintosh': 'macintosh',
        'macroman': 'macintosh',
        'x-mac-roman': 'macintosh',
        'mac': 'macintosh',
        
        # Другие распространенные кодировки
        'cp866': 'cp866',
        'koi8-r': 'koi8-r',
        'koi8_r': 'koi8-r',
        'koi8r': 'koi8-r',
        'iso-8859-1': 'iso-8859-1',
        'latin1': 'iso-8859-1',
        'ascii': 'ascii',
    }
    
    def __init__(self, use_chardet: bool = True, sample_size: int = 4096):
        """
        Инициализация поисковика
        
        Args:
            use_chardet: Использовать библиотеку chardet для определения кодировки
            sample_size: Размер сэмпла для анализа кодировки (в байтах)
        """
        self.use_chardet = use_chardet and CHARDET_AVAILABLE
        self.sample_size = sample_size
        
        if use_chardet and not CHARDET_AVAILABLE:
            print("Предупреждение: chardet не установлен. Используется простой метод определения кодировки.")
            print("Установите: pip install chardet")
    
    def normalize_encoding(self, encoding: str) -> str:
        """Нормализация названия кодировки"""
        if not encoding:
            return ''
        
        encoding_lower = encoding.lower()
        return self.ENCODING_ALIASES.get(encoding_lower, encoding_lower)
    
    def detect_encoding_chardet(self, file_path: str) -> Optional[str]:
        """Определение кодировки с помощью chardet"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(self.sample_size)
            
            if not raw_data:
                return None
            
            result = chardet.detect(raw_data)
            return result['encoding']
        except Exception as e:
            print(f"Ошибка при определении кодировки файла {file_path}: {e}", file=sys.stderr)
            return None
    
    def detect_encoding_simple(self, file_path: str, target_encodings: List[str]) -> Optional[str]:
        """Простой метод определения кодировки - пробуем прочитать файл в разных кодировках"""
        target_encodings = [self.normalize_encoding(enc) for enc in target_encodings]
        
        for encoding in target_encodings:
            try:
                # Пробуем прочитать файл с указанной кодировкой
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    f.read(1024)  # Читаем небольшой кусок
                return encoding
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        return None
    
    def detect_encoding(self, file_path: str, target_encodings: Optional[List[str]] = None) -> Optional[str]:
        """Определение кодировки файла"""
        if self.use_chardet:
            detected = self.detect_encoding_chardet(file_path)
            if detected:
                normalized = self.normalize_encoding(detected)
                # Если заданы целевые кодировки, проверяем соответствие
                if target_encodings:
                    target_normalized = [self.normalize_encoding(enc) for enc in target_encodings]
                    if normalized in target_normalized:
                        return normalized
                else:
                    return normalized
            return None
        else:
            if target_encodings:
                return self.detect_encoding_simple(file_path, target_encodings)
            else:
                # Без chardet и без целевых кодировок не можем определить
                return None
    
    def find_files(
        self,
        root_dir: str,
        extensions: Optional[List[str]] = None,
        encodings: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        min_size: int = 0,
        max_size: Optional[int] = None
    ) -> List[FileInfo]:
        """
        Рекурсивный поиск файлов с заданными параметрами
        
        Args:
            root_dir: Корневая директория для поиска
            extensions: Список расширений файлов (с точкой, например .txt)
            encodings: Список кодировок для поиска
            exclude_dirs: Список директорий для исключения
            min_size: Минимальный размер файла в байтах
            max_size: Максимальный размер файла в байтах
            
        Returns:
            Список объектов FileInfo
        """
        root_path = Path(root_dir)
        if not root_path.exists():
            raise FileNotFoundError(f"Директория не найдена: {root_dir}")
        if not root_path.is_dir():
            raise NotADirectoryError(f"Путь не является директорией: {root_dir}")
        
        # Нормализуем расширения
        if extensions:
            extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
        
        # Нормализуем кодировки
        if encodings:
            encodings = [self.normalize_encoding(enc) for enc in encodings]
        
        # Множество для исключения директорий
        exclude_set = set(exclude_dirs) if exclude_dirs else set()
        
        found_files = []
        
        for item in root_path.rglob('*'):
            # Пропускаем исключенные директории
            if any(excluded in str(item) for excluded in exclude_set):
                continue
            
            if item.is_file():
                # Проверяем расширение
                if extensions:
                    if item.suffix.lower() not in extensions:
                        continue
                
                # Проверяем размер
                try:
                    file_size = item.stat().st_size
                except (OSError, PermissionError):
                    continue
                
                if file_size < min_size:
                    continue
                if max_size and file_size > max_size:
                    continue
                
                # Определяем кодировку
                try:
                    encoding = self.detect_encoding(str(item), encodings)
                except (PermissionError, OSError):
                    continue
                
                if encoding:
                    # Если заданы конкретные кодировки, проверяем вхождение
                    if encodings:
                        if encoding not in encodings:
                            continue
                    
                    file_info = FileInfo(
                        path=str(item),
                        encoding=encoding,
                        size=file_size,
                        extension=item.suffix.lower(),
                        directory=str(item.parent)
                    )
                    found_files.append(file_info)
        
        return found_files
    
    def save_results(
        self,
        files: List[FileInfo],
        output_format: str = 'txt',
        output_file: str = 'found_files'
    ) -> str:
        """
        Сохранение результатов в файл
        
        Args:
            files: Список найденных файлов
            output_format: Формат вывода (txt, json, csv)
            output_file: Имя выходного файла (без расширения)
            
        Returns:
            Путь к сохраненному файлу
        """
        output_format = output_format.lower()
        
        if output_format == 'json':
            output_path = f"{output_file}.json"
            data = [file.to_dict() for file in files]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        elif output_format == 'csv':
            output_path = f"{output_file}.csv"
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Путь', 'Кодировка', 'Размер (байт)', 'Расширение', 'Директория'])
                for file in files:
                    writer.writerow([file.path, file.encoding, file.size, file.extension, file.directory])
        
        else:  # txt по умолчанию
            output_path = f"{output_file}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Найдено файлов: {len(files)}\n")
                f.write("=" * 60 + "\n\n")
                for i, file in enumerate(files, 1):
                    f.write(f"{i}. {file.path}\n")
                    f.write(f"   Кодировка: {file.encoding}\n")
                    f.write(f"   Размер: {file.size} байт\n")
                    f.write(f"   Расширение: {file.extension}\n")
                    f.write(f"   Директория: {file.directory}\n")
                    f.write("-" * 40 + "\n")
        
        return output_path
    
    def print_results_simple(self, files: List[FileInfo]):
        """Простой вывод результатов в формате 'путь: кодировка'"""
        for file in files:
            print(f"{file.path}: {file.encoding}")
    
    def print_results_detailed(self, files: List[FileInfo], limit: Optional[int] = None):
        """Подробный вывод результатов"""
        print(f"\nНайдено файлов: {len(files)}")
        print("=" * 60)
        
        if limit and len(files) > limit:
            print(f"Показаны первые {limit} файлов:")
            files_to_show = files[:limit]
        else:
            files_to_show = files
        
        for i, file in enumerate(files_to_show, 1):
            print(f"\n{i}. {file.path}")
            print(f"   Кодировка: {file.encoding}")
            print(f"   Размер: {file.size} байт")
            print(f"   Расширение: {file.extension}")
            print(f"   Директория: {file.directory}")


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Рекурсивный поиск файлов по кодировкам',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s /путь/к/папке --encodings utf8 win1251
  %(prog)s /путь/к/папке -e .txt .csv -c utf8 -o results.json --format json
  %(prog)s /путь/к/папке --extensions .txt --min-size 1024 --exclude-dir temp
        """
    )
    
    parser.add_argument(
        'root_dir',
        help='Корневая директория для поиска'
    )
    
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        help='Расширения файлов (например: .txt .csv .json)'
    )
    
    parser.add_argument(
        '-c', '--encodings',
        nargs='+',
        default=['utf8', 'win1251', 'macintosh'],
        help='Кодировки для поиска (по умолчанию: utf8 win1251 macintosh)'
    )
    
    parser.add_argument(
        '-x', '--exclude-dir',
        nargs='+',
        help='Директории для исключения (например: .git node_modules)'
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=0,
        help='Минимальный размер файла в байтах'
    )
    
    parser.add_argument(
        '--max-size',
        type=int,
        help='Максимальный размер файла в байтах'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Имя выходного файла (без расширения). Если указан, результаты сохраняются в файл'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['txt', 'json', 'csv'],
        default='txt',
        help='Формат выходного файла (используется с --output)'
    )
    
    parser.add_argument(
        '--no-chardet',
        action='store_true',
        help='Не использовать chardet (только простой метод)'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=4096,
        help='Размер сэмпла для определения кодировки (в байтах)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод в консоль'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Тихий режим, выводит только путь и кодировку'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Ограничить количество выводимых файлов'
    )
    
    return parser.parse_args()


def main():
    """Точка входа для командной строки"""
    args = parse_arguments()
    
    try:
        # Создаем экземпляр поисковика
        finder = FileEncodingFinder(
            use_chardet=not args.no_chardet,
            sample_size=args.sample_size
        )
        
        if args.verbose and not args.quiet:
            print(f"Поиск файлов в: {args.root_dir}")
            print(f"Расширения: {args.extensions or 'все'}")
            print(f"Кодировки: {args.encodings}")
            if args.exclude_dir:
                print(f"Исключаемые директории: {args.exclude_dir}")
            if args.min_size > 0:
                print(f"Минимальный размер: {args.min_size} байт")
            if args.max_size:
                print(f"Максимальный размер: {args.max_size} байт")
            print("=" * 60)
        
        # Выполняем поиск
        files = finder.find_files(
            root_dir=args.root_dir,
            extensions=args.extensions,
            encodings=args.encodings,
            exclude_dirs=args.exclude_dir,
            min_size=args.min_size,
            max_size=args.max_size
        )
        
        # Выводим результаты
        if files:
            # Сохраняем в файл, если указан output
            if args.output:
                output_path = finder.save_results(files, args.format, args.output)
                if not args.quiet:
                    print(f"Результаты сохранены в: {output_path}")
            
            # Вывод в консоль
            if not args.quiet:
                if args.verbose:
                    finder.print_results_detailed(files, args.limit)
                else:
                    # Вывод по умолчанию: только путь и кодировка
                    finder.print_results_simple(files)
            
            # Если quiet режим, выводим только путь:кодировка
            if args.quiet:
                finder.print_results_simple(files)
                
        else:
            if not args.quiet:
                print("Файлов с заданными параметрами не найдено.")
            
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def find_files_cli():
    """Функция для запуска из setup.py или других скриптов"""
    main()


# Пример использования как библиотеки
if __name__ == "__main__":
    main()