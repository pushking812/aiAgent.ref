import shutil
import os
import glob
import json
import argparse
from pathlib import Path
import sys

def load_config(config_path=None):
    """
    Загрузка конфигурации из файла.
    
    Args:
        config_path: Путь к конфигурационному файлу
        
    Returns:
        Словарь с настройками или значения по умолчанию
    """
    default_config = {
        "patterns": [
            "**/__pycache__",
            "**/.pytest_cache", 
            "**/.coverage",
            "**/coverage_html",
            "**/htmlcov",
            "**/.mypy_cache",
            "**/.tox",
            "**/*.egg-info",
            "**/build",
            "**/dist"
        ]
    }
    
    # Если путь к конфигу не указан, ищем в стандартных местах
    if config_path is None:
        possible_paths = [
            "clean_config.json",
            ".clean_config.json",
            "config/clean_config.json",
            os.path.expanduser("~/.clean_config.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
    elif not os.path.exists(config_path):
        print(f"Предупреждение: конфигурационный файл {config_path} не найден")
        return default_config
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Объединяем с конфигом по умолчанию
            if "patterns" in user_config:
                default_config["patterns"] = user_config["patterns"]
            
            print(f"Загружена конфигурация из: {config_path}")
            return default_config
        except json.JSONDecodeError as e:
            print(f"Ошибка чтения конфигурационного файла {config_path}: {e}")
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
    
    return default_config

def save_config(config, config_path="clean_config.json"):
    """
    Сохранение конфигурации в файл.
    
    Args:
        config: Словарь с конфигурацией
        config_path: Путь для сохранения
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Конфигурация сохранена в: {config_path}")
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")

def clean_cache(roots=None, exclude=None, config_path=None, patterns=None):
    """
    Очистка кэш-файлов и временных директорий.
    
    Args:
        roots: Список корневых папок для поиска
        exclude: Список папок для исключения из поиска
        config_path: Путь к конфигурационному файлу
        patterns: Список паттернов для удаления (переопределяет конфиг)
    """
    if roots is None:
        roots = ["."]
    if exclude is None:
        exclude = []
    
    # Загружаем конфигурацию
    config = load_config(config_path)
    
    # Используем переданные паттерны или из конфига
    if patterns is None:
        patterns = config.get("patterns", [])
    
    if not patterns:
        print("Предупреждение: список паттернов для удаления пуст!")
        return
    
    # Преобразуем пути в абсолютные для сравнения
    exclude_paths = [Path(p).resolve() for p in exclude]
    
    print(f"Используемые паттерны: {patterns}")
    
    for root in roots:
        if not os.path.exists(root):
            print(f"Предупреждение: папка {root} не существует, пропускаем")
            continue
            
        print(f"\nПоиск в папке: {root}")
        items_found = 0
        
        for pattern in patterns:
            # Обрабатываем относительные и абсолютные пути в паттернах
            if pattern.startswith("/") or pattern.startswith("~"):
                # Абсолютный путь или путь от домашней директории
                search_pattern = os.path.expanduser(pattern)
            else:
                # Относительный путь
                search_pattern = os.path.join(root, pattern)
            
            try:
                for path in glob.glob(search_pattern, recursive=True):
                    # Проверяем, не находится ли путь в исключенной папке
                    if exclude_paths:
                        abs_path = Path(path).resolve()
                        is_excluded = False
                        
                        for excluded in exclude_paths:
                            # Проверяем, находится ли путь внутри исключенной папки
                            try:
                                if excluded in abs_path.parents or abs_path == excluded:
                                    is_excluded = True
                                    break
                            except:
                                pass
                        
                        if is_excluded:
                            continue
                    
                    items_found += 1
                    
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path, ignore_errors=True)
                            print(f"  Удалена папка: {path}")
                        else:
                            os.remove(path)
                            print(f"  Удален файл: {path}")
                    except Exception as e:
                        print(f"  Ошибка при удалении {path}: {e}")
            except Exception as e:
                print(f"  Ошибка при обработке паттерна {pattern}: {e}")
        
        if items_found == 0:
            print("  Совпадений не найдено")

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Очистка кэш-файлов и временных директорий Python проектов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python clean.py -d ./project1 ./project2
  python clean.py -e ./venv ./node_modules
  python clean.py --config my_config.json
  python clean.py --show-config
  python clean.py --add-pattern "**/.cache"
        """
    )
    
    parser.add_argument(
        "-d", "--directories",
        nargs="+",
        default=["."],
        help="Корневые папки для поиска (по умолчанию: текущая папка)"
    )
    
    parser.add_argument(
        "-e", "--exclude",
        nargs="+",
        default=[],
        help="Папки для исключения из поиска"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Путь к конфигурационному файлу"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать что будет удалено без фактического удаления"
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Показать текущую конфигурацию и выйти"
    )
    
    parser.add_argument(
        "--add-pattern",
        nargs="+",
        help="Добавить паттерн(ы) к текущей конфигурации"
    )
    
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Сбросить конфигурацию к значениям по умолчанию"
    )
    
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="Показать все активные паттерны"
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Обработка специальных команд
    if args.show_config:
        config = load_config(args.config)
        print("Текущая конфигурация:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    if args.reset_config:
        default_config = {
            "patterns": [
                "**/__pycache__",
                "**/.pytest_cache",
                "**/.coverage",
                "**/coverage_html",
                "**/htmlcov",
                "**/.mypy_cache",
                "**/.tox",
                "**/*.egg-info",
                "**/build",
                "**/dist"
            ]
        }
        save_config(default_config, args.config or "clean_config.json")
        print("Конфигурация сброшена к значениям по умолчанию")
        sys.exit(0)
    
    if args.add_pattern:
        config = load_config(args.config)
        current_patterns = config.get("patterns", [])
        
        for pattern in args.add_pattern:
            if pattern not in current_patterns:
                current_patterns.append(pattern)
                print(f"Добавлен паттерн: {pattern}")
            else:
                print(f"Паттерн уже существует: {pattern}")
        
        config["patterns"] = current_patterns
        save_config(config, args.config or "clean_config.json")
        sys.exit(0)
    
    if args.list_patterns:
        config = load_config(args.config)
        patterns = config.get("patterns", [])
        print("Активные паттерны:")
        for i, pattern in enumerate(patterns, 1):
            print(f"  {i}. {pattern}")
        sys.exit(0)
    
    # Основной режим работы
    print(f"Корневые папки для поиска: {args.directories}")
    if args.exclude:
        print(f"Исключаемые папки: {args.exclude}")
    
    if args.dry_run:
        print("\nРЕЖИМ ПРОСМОТРА (dry-run): файлы не будут удалены")
        
        config = load_config(args.config)
        patterns = config.get("patterns", [])
        
        for root in args.directories:
            if not os.path.exists(root):
                print(f"Предупреждение: папка {root} не существует, пропускаем")
                continue
                
            print(f"\nПоиск в папке: {root}")
            
            exclude_paths = [Path(p).resolve() for p in args.exclude]
            
            for pattern in patterns:
                if pattern.startswith("/") or pattern.startswith("~"):
                    search_pattern = os.path.expanduser(pattern)
                else:
                    search_pattern = os.path.join(root, pattern)
                
                try:
                    for path in glob.glob(search_pattern, recursive=True):
                        if args.exclude:
                            abs_path = Path(path).resolve()
                            is_excluded = False
                            
                            for excluded in exclude_paths:
                                try:
                                    if excluded in abs_path.parents or abs_path == excluded:
                                        is_excluded = True
                                        break
                                except:
                                    pass
                            
                            if is_excluded:
                                continue
                        
                        if os.path.isdir(path):
                            print(f"  [ПАПКА] {path}")
                        else:
                            print(f"  [ФАЙЛ] {path}")
                except Exception as e:
                    print(f"  Ошибка при обработке паттерна {pattern}: {e}")
    else:
        clean_cache(
            roots=args.directories,
            exclude=args.exclude,
            config_path=args.config
        )
    
    print("\nОчистка завершена!")

if __name__ == "__main__":
    main()