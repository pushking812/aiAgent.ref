#!/usr/bin/env python3
"""
Рекурсивный поиск файлов по кодировкам с использованием charset-normalizer.
Наиболее надежный метод определения кодировок.
Включает скрытые файлы и папки.
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import csv

try:
    from charset_normalizer import from_bytes, detect
    CHARSET_NORMALIZER_AVAILABLE = True
except ImportError:
    CHARSET_NORMALIZER_AVAILABLE = False

@dataclass
class FileInfo:
    """Информация о найденном файле"""
    path: str
    encoding: str
    size: int
    extension: str
    directory: str
    confidence: float = 0.0
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return asdict(self)

class FileEncodingFinder:
    """Класс для поиска файлов по кодировкам с использованием charset-normalizer"""
    
    # Карта алиасов кодировок для нормализации
    ENCODING_ALIASES = {
        # UTF-8
        'utf8': 'utf-8',
        'utf-8': 'utf-8',
        'utf_8': 'utf-8',
        'utf8-sig': 'utf-8-sig',
        'utf-8-sig': 'utf-8-sig',
        
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
        'utf-16': 'utf-16',
        'utf-16le': 'utf-16-le',
        'utf-16be': 'utf-16-be',
        'utf-32': 'utf-32',
    }
    
    def __init__(self, sample_size: int = 8192, include_hidden: bool = True):
        """
        Инициализация поисковика
        
        Args:
            sample_size: Размер сэмпла для анализа кодировки (в байтах)
            include_hidden: Включать ли скрытые файлы и папки в поиск
        """
        self.sample_size = sample_size
        self.include_hidden = include_hidden
        
        if not CHARSET_NORMALIZER_AVAILABLE:
            print("Ошибка: библиотека charset-normalizer не установлена.")
            print("Установите: pip install charset-normalizer")
            sys.exit(1)
    
    def normalize_encoding(self, encoding: str) -> str:
        """Нормализация названия кодировки"""
        if not encoding:
            return ''
        
        encoding_lower = encoding.lower().replace('_', '-')
        return self.ENCODING_ALIASES.get(encoding_lower, encoding_lower)
    
    def check_bom(self, data: bytes) -> Optional[str]:
        """Проверка BOM (Byte Order Mark) в данных - самый надежный метод"""
        # UTF-8 BOM
        if data.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        # UTF-16 BE BOM
        elif data.startswith(b'\xfe\xff'):
            return 'utf-16-be'
        # UTF-16 LE BOM
        elif data.startswith(b'\xff\xfe'):
            return 'utf-16-le'
        # UTF-32 BE BOM
        elif data.startswith(b'\x00\x00\xfe\xff'):
            return 'utf-32-be'
        # UTF-32 LE BOM
        elif data.startswith(b'\xff\xfe\x00\x00'):
            return 'utf-32-le'
        return None
    
    def detect_encoding_with_charset_normalizer(self, data: bytes) -> Optional[Tuple[str, float]]:
        """Определение кодировки с помощью charset-normalizer"""
        try:
            # Сначала пробуем быстрый метод detect
            result = detect(data)
            if result and result.get('encoding'):
                encoding = self.normalize_encoding(result['encoding'])
                confidence = result.get('confidence', 0.0)
                return encoding, confidence
            
            # Если detect не дал уверенного результата, используем from_bytes
            result = from_bytes(data).best()
            if result:
                encoding = self.normalize_encoding(result.encoding)
                confidence = result.coherence  # Мера согласованности
                return encoding, confidence
                
        except Exception as e:
            print(f"Ошибка определения кодировки: {e}", file=sys.stderr)
        
        return None
    
    def detect_encoding(self, file_path: str, target_encodings: Optional[List[str]] = None) -> Optional[Tuple[str, float]]:
        """
        Определение кодировки файла с помощью charset-normalizer
        
        Returns:
            Tuple(encoding, confidence) или None
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read(self.sample_size)
            
            if not data:
                return None
            
            # Проверяем BOM (самый надежный метод) - уверенность 100%
            bom_encoding = self.check_bom(data)
            if bom_encoding:
                # Если есть целевые кодировки, проверяем соответствие
                if target_encodings:
                    target_normalized = [self.normalize_encoding(enc) for enc in target_encodings]
                    if bom_encoding in target_normalized:
                        return bom_encoding, 1.0
                else:
                    return bom_encoding, 1.0
            
            # Используем charset-normalizer
            result = self.detect_encoding_with_charset_normalizer(data)
            
            if result:
                detected_encoding, confidence = result
                
                # Если заданы целевые кодировки, проверяем соответствие
                if target_encodings:
                    target_normalized = [self.normalize_encoding(enc) for enc in target_encodings]
                    if detected_encoding in target_normalized:
                        return detected_encoding, confidence
                else:
                    return detected_encoding, confidence
            
            return None
                
        except (IOError, OSError, PermissionError) as e:
            print(f"Ошибка чтения файла {file_path}: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Неожиданная ошибка при обработке файла {file_path}: {e}", file=sys.stderr)
            return None
    
    def is_excluded(self, item_path: Path, root_path: Path, exclude_set: Set[str]) -> bool:
        """Проверяет, исключена ли директория или файл"""
        if not exclude_set:
            return False
        
        # Получаем относительный путь от корневой директории
        try:
            rel_path = item_path.relative_to(root_path)
        except ValueError:
            # Если не удается получить относительный путь, используем абсолютный
            rel_path = Path(item_path)
        
        # Проверяем каждый компонент пути
        for part in rel_path.parts:
            if part in exclude_set:
                return True
        
        # Также проверяем полный относительный путь как строку
        rel_path_str = str(rel_path)
        for excluded in exclude_set:
            # Проверяем, что исключаемая директория является частью пути
            # и находится в начале пути или после разделителя
            if rel_path_str == excluded or \
               rel_path_str.startswith(excluded + os.sep) or \
               os.sep + excluded + os.sep in rel_path_str:
                return True
        
        return False
    
    def is_hidden(self, path: Path) -> bool:
        """Проверяет, является ли файл или папка скрытой"""
        # Для Windows
        if os.name == 'nt':
            try:
                # Получаем атрибуты файла
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
                # FILE_ATTRIBUTE_HIDDEN = 0x2
                return attrs & 0x2 != 0
            except Exception:
                # Если не удалось получить атрибуты, проверяем по имени
                name = path.name
                return name.startswith('.') or name.startswith('~')
        
        # Для Unix-подобных систем
        else:
            # Проверяем, начинается ли имя с точки
            name = path.name
            return name.startswith('.') or name.startswith('~')
    
    def should_include_file(self, file_path: Path, extensions: Optional[List[str]]) -> bool:
        """
        Проверяет, соответствует ли файл заданным расширениям
        
        Args:
            file_path: Путь к файлу
            extensions: Список расширений (с точкой или без), или None для всех файлов
            
        Returns:
            True если файл соответствует расширениям или extensions=None
        """
        if extensions is None:
            return True
        
        # Получаем расширение файла (включая точку, если есть)
        file_ext = file_path.suffix.lower()
        
        # Для каждого расширения в списке
        for ext in extensions:
            ext = ext.strip().lower()
            
            # Если указано "." или пустая строка - ищем файлы без расширения
            if ext == '.' or ext == '':
                if file_ext == '':
                    return True
            # Если указано расширение с точкой
            elif ext.startswith('.'):
                if file_ext == ext:
                    return True
            # Если указано расширение без точки
            else:
                if file_ext == f'.{ext}':
                    return True
        
        return False
    
    def find_files(
        self,
        root_dir: str,
        extensions: Optional[List[str]] = None,
        encodings: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        min_size: int = 0,
        max_size: Optional[int] = None,
        min_confidence: float = 0.0,
        exclude_hidden: bool = False,
        debug: bool = False
    ) -> List[FileInfo]:
        """
        Рекурсивный поиск файлов с заданными параметрами
        
        Args:
            root_dir: Корневая директория для поиска
            extensions: Список расширений файлов (можно указывать с точкой или без)
                       '.' или '' - файлы без расширения
                       None - все файлы
            encodings: Список кодировок для поиска
            exclude_dirs: Список директорий для исключения
            min_size: Минимальный размер файла в байтах
            max_size: Максимальный размер файла в байтах
            min_confidence: Минимальная уверенность в определении кодировки
            exclude_hidden: Исключать ли скрытые файлы и папки
            debug: Включить отладочный вывод
            
        Returns:
            Список объектов FileInfo
        """
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            raise FileNotFoundError(f"Директория не найдена: {root_dir}")
        if not root_path.is_dir():
            raise NotADirectoryError(f"Путь не является директорией: {root_dir}")
        
        # Нормализуем кодировки
        if encodings:
            encodings = [self.normalize_encoding(enc) for enc in encodings]
        
        # Множество для исключения директорий
        exclude_set = set(exclude_dirs) if exclude_dirs else set()
        
        found_files = []
        
        if debug:
            print(f"DEBUG: Начинаем поиск в {root_path}")
            print(f"DEBUG: Расширения: {extensions}")
            print(f"DEBUG: Кодировки: {encodings}")
        
        # Используем os.walk для лучшего контроля над исключением директорий
        for root, dirs, files in os.walk(root_path, topdown=True):
            # Преобразуем root в Path для удобства
            current_dir = Path(root)
            
            if debug and len(found_files) < 10:  # Лимитируем отладочный вывод
                print(f"DEBUG: Проверяем директорию {current_dir}")
                print(f"DEBUG: Файлов в директории: {len(files)}")
            
            # Фильтруем директории и файлы
            filtered_dirs = []
            for d in dirs:
                dir_path = current_dir / d
                
                # Проверяем исключение директорий
                if self.is_excluded(dir_path, root_path, exclude_set):
                    continue
                
                # Проверяем скрытость
                if exclude_hidden and self.is_hidden(dir_path):
                    continue
                
                filtered_dirs.append(d)
            
            # Обновляем список директорий для дальнейшего обхода
            dirs[:] = filtered_dirs
            
            for file in files:
                file_path = current_dir / file
                
                # Проверяем скрытость
                if exclude_hidden and self.is_hidden(file_path):
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Пропускаем скрытый файл {file_path}")
                    continue
                
                # Проверяем, не находится ли файл в исключенной директории
                if self.is_excluded(file_path, root_path, exclude_set):
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Пропускаем файл в исключенной директории {file_path}")
                    continue
                
                # Проверяем расширение
                if extensions is not None:
                    # Получаем расширение файла
                    file_ext = file_path.suffix.lower()
                    
                    # Флаг для проверки соответствия
                    matches_extension = False
                    
                    # Для каждого расширения в списке
                    for ext in extensions:
                        ext = ext.strip().lower()
                        
                        # Если указано "." или пустая строка - ищем файлы без расширения
                        if ext == '.' or ext == '':
                            if file_ext == '':
                                matches_extension = True
                                break
                        # Если указано расширение с точкой
                        elif ext.startswith('.'):
                            if file_ext == ext:
                                matches_extension = True
                                break
                        # Если указано расширение без точки
                        else:
                            if file_ext == f'.{ext}':
                                matches_extension = True
                                break
                    
                    if not matches_extension:
                        if debug and len(found_files) < 10:
                            print(f"DEBUG: Пропускаем файл {file_path} - не соответствует расширениям {extensions}")
                        continue
                
                # Проверяем размер
                try:
                    file_size = file_path.stat().st_size
                except (OSError, PermissionError):
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Не удалось получить размер файла {file_path}")
                    continue
                
                if file_size < min_size:
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Пропускаем файл {file_path} - размер {file_size} меньше минимального {min_size}")
                    continue
                if max_size and file_size > max_size:
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Пропускаем файл {file_path} - размер {file_size} больше максимального {max_size}")
                    continue
                
                # Определяем кодировку
                try:
                    result = self.detect_encoding(str(file_path), encodings)
                except (PermissionError, OSError) as e:
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Ошибка доступа к файлу {file_path}: {e}")
                    continue
                
                if result:
                    detected_encoding, confidence = result
                    
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Определили кодировку для {file_path}: {detected_encoding} (уверенность: {confidence:.2%})")
                    
                    # Проверяем уверенность
                    if confidence < min_confidence:
                        if debug and len(found_files) < 10:
                            print(f"DEBUG: Пропускаем файл {file_path} - уверенность {confidence:.2%} меньше минимальной {min_confidence}")
                        continue
                    
                    # Если заданы конкретные кодировки, проверяем вхождение
                    if encodings:
                        if detected_encoding not in encodings:
                            if debug and len(found_files) < 10:
                                print(f"DEBUG: Пропускаем файл {file_path} - кодировка {detected_encoding} не в списке {encodings}")
                            continue
                    
                    # Определяем расширение для вывода
                    if file_path.suffix:
                        file_extension = file_path.suffix.lower()
                    else:
                        file_extension = "(без расширения)"
                    
                    file_info = FileInfo(
                        path=str(file_path),
                        encoding=detected_encoding,
                        size=file_size,
                        extension=file_extension,
                        directory=str(file_path.parent),
                        confidence=confidence
                    )
                    found_files.append(file_info)
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Добавили файл {file_path}")
                else:
                    if debug and len(found_files) < 10:
                        print(f"DEBUG: Не удалось определить кодировку для {file_path}")
        
        if debug:
            print(f"DEBUG: Всего найдено файлов: {len(found_files)}")
        
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
                writer.writerow(['Путь', 'Кодировка', 'Уверенность', 'Размер (байт)', 'Расширение', 'Директория'])
                for file in files:
                    writer.writerow([
                        file.path, 
                        file.encoding, 
                        f"{file.confidence:.2%}",
                        file.size, 
                        file.extension, 
                        file.directory
                    ])
        
        else:  # txt по умолчанию
            output_path = f"{output_file}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Найдено файлов: {len(files)}\n")
                f.write("=" * 60 + "\n\n")
                for i, file in enumerate(files, 1):
                    f.write(f"{i}. {file.path}\n")
                    f.write(f"   Кодировка: {file.encoding}\n")
                    f.write(f"   Уверенность: {file.confidence:.2%}\n")
                    f.write(f"   Размер: {file.size} байт\n")
                    f.write(f"   Расширение: {file.extension}\n")
                    f.write(f"   Директория: {file.directory}\n")
                    f.write("-" * 40 + "\n")
        
        return output_path
    
    def print_results_simple(self, files: List[FileInfo], show_confidence: bool = False):
        """Простой вывод результатов в формате 'путь: кодировка'"""
        for file in files:
            if show_confidence:
                print(f"{file.path}: {file.encoding} ({file.confidence:.2%})")
            else:
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
            print(f"   Уверенность: {file.confidence:.2%}")
            print(f"   Размер: {file.size} байт")
            print(f"   Расширение: {file.extension}")
            print(f"   Директория: {file.directory}")


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Рекурсивный поиск файлов по кодировкам (использует charset-normalizer)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s /путь/к/папке --encodings utf8 win1251 macintosh
  %(prog)s /путь/к/папке -e .txt .csv --confidence 0.8
  %(prog)s /путь/к/папке --sample-size 16384 --no-validation
  %(prog)s /путь/к/папке -x node_modules .git  # исключить директории
  %(prog)s /путь/к/папке -e .  # найти файлы без расширения
  %(prog)s /путь/к/папке -e .txt .  # файлы с расширением .txt и без расширения
  %(prog)s /путь/к/папке -e txt py  # можно указывать без точки
  %(prog)s /путь/к/папке --exclude-hidden  # исключить скрытые файлы
  %(prog)s /путь/к/папке --debug  # включить отладочный вывод
  
Форматы указания расширений:
  .txt    - файлы с расширением .txt
  txt     - тоже файлы с расширением .txt  
  .       - файлы без расширения
  (пусто) - файлы без расширения (при редактировании списка)
  
Если -e не указан, ищутся все файлы (с любыми расширениями и без них).
По умолчанию включены скрытые файлы и папки.
        """
    )
    
    parser.add_argument(
        'root_dir',
        help='Корневая директория для поиска'
    )
    
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        help='Расширения файлов (например: .txt .csv .json .) - точка для файлы без расширения'
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
        '--confidence',
        type=float,
        default=0.0,
        help='Минимальная уверенность в определении кодировки (от 0.0 до 1.0)'
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
        '--sample-size',
        type=int,
        default=8192,
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
    
    parser.add_argument(
        '--show-confidence',
        action='store_true',
        help='Показывать уверенность в определении кодировки'
    )
    
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Устаревший параметр, оставлен для совместимости'
    )
    
    parser.add_argument(
        '--exclude-hidden',
        action='store_true',
        help='Исключить скрытые файлы и папки из поиска'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Включить отладочный вывод'
    )
    
    return parser.parse_args()


def main():
    """Точка входа для командной строки"""
    args = parse_arguments()
    
    # Проверяем доступность charset-normalizer
    if not CHARSET_NORMALIZER_AVAILABLE:
        print("Ошибка: библиотека charset-normalizer не установлена.")
        print("Установите: pip install charset-normalizer")
        sys.exit(1)
    
    try:
        # Создаем экземпляр поисковика
        finder = FileEncodingFinder(sample_size=args.sample_size)
        
        # Формируем строку для вывода расширений
        extensions_display = "все файлы"
        if args.extensions:
            extensions_display = args.extensions
        
        if (args.verbose or args.debug) and not args.quiet:
            print(f"Поиск файлов в: {args.root_dir}")
            print(f"Расширения: {extensions_display}")
            print(f"Кодировки: {args.encodings}")
            print(f"Библиотека: charset-normalizer")
            if args.exclude_dir:
                print(f"Исключаемые директории: {args.exclude_dir}")
            if args.min_size > 0:
                print(f"Минимальный размер: {args.min_size} байт")
            if args.max_size:
                print(f"Максимальный размер: {args.max_size} байт")
            if args.confidence > 0:
                print(f"Минимальная уверенность: {args.confidence:.0%}")
            print(f"Размер сэмпла: {args.sample_size} байт")
            print(f"Скрытые файлы: {'исключены' if args.exclude_hidden else 'включены'}")
            print(f"Режим отладки: {'включен' if args.debug else 'выключен'}")
            print("=" * 60)
        
        # Выполняем поиск
        files = finder.find_files(
            root_dir=args.root_dir,
            extensions=args.extensions,
            encodings=args.encodings,
            exclude_dirs=args.exclude_dir,
            min_size=args.min_size,
            max_size=args.max_size,
            min_confidence=args.confidence,
            exclude_hidden=args.exclude_hidden,
            debug=args.debug
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
                    # Вывод по умолчанию: путь и кодировка (с уверенностью если нужно)
                    finder.print_results_simple(files, args.show_confidence)
            
            # Если quiet режим, выводим только путь:кодировка
            if args.quiet:
                finder.print_results_simple(files, args.show_confidence)
                
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