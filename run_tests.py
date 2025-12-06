#!/usr/bin/env python3
# run_tests.py

import subprocess
import sys
import os
import argparse


def run_tests(args):
    """Запускает тесты с указанными параметрами."""
    cmd = [sys.executable, "-m", "pytest", "tests/"]
    
    # Добавляем общие опции
    cmd.extend(["-v", "--tb=short", "--disable-warnings"])
    
    # Добавляем пользовательские опции
    if args.marker:
        cmd.extend(["-m", args.marker])
    
    if args.runslow:
        cmd.append("--runslow")
    
    if args.coverage:
        cmd.extend([
            "--cov=gui.views",
            "--cov-report=term",
            "--cov-report=html:coverage_html"
        ])
        
        # Добавляем минимальное покрытие для отчета
        if args.min_coverage:
            cmd.extend([f"--cov-fail-under={args.min_coverage}"])
    
    # Добавляем конкретные тесты если указаны
    if args.test_files:
        cmd.extend(args.test_files)
    
    print(f"🚀 Запуск тестов...")
    print(f"📋 Команда: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ Все тесты пройдены успешно!")
    else:
        print(f"❌ Тесты завершились с ошибкой (код: {result.returncode})")
    
    return result.returncode


def show_coverage(directory="coverage_html"):
    """Показывает отчет о покрытии."""
    if not os.path.exists(directory):
        print(f"📊 Отчет о покрытии не найден в {directory}")
        return
    
    import webbrowser
    index_file = os.path.join(directory, "index.html")
    
    if os.path.exists(index_file):
        print(f"📊 Отчет о покрытии сгенерирован: {os.path.abspath(index_file)}")
        if input("Открыть в браузере? (y/n): ").lower() == 'y':
            webbrowser.open(f"file://{os.path.abspath(index_file)}")


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Запуск тестов GUI приложения")
    
    parser.add_argument(
        "-m", "--marker",
        help="Запустить тесты с указанным маркером (gui, unit, integration)"
    )
    
    parser.add_argument(
        "--runslow",
        action="store_true",
        help="Запускать медленные тесты"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Включить отчет о покрытии кода"
    )
    
    parser.add_argument(
        "--min-coverage",
        type=int,
        default=50,
        help="Минимальный процент покрытия (по умолчанию: 50%%)"
    )
    
    parser.add_argument(
        "--show-html",
        action="store_true",
        help="Показать HTML отчет о покрытии в браузере"
    )
    
    parser.add_argument(
        "test_files",
        nargs="*",
        help="Конкретные тестовые файлы для запуска"
    )
    
    args = parser.parse_args()
    
    # Если не указаны аргументы, показываем справку
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n📋 Примеры использования:")
        print("  python run_tests.py --coverage              # Все тесты с покрытием")
        print("  python run_tests.py -m gui --coverage       # GUI тесты с покрытием")
        print("  python run_tests.py -m unit                 # Только unit-тесты")
        print("  python run_tests.py -m gui --runslow        # GUI тесты включая медленные")
        print("  python run_tests.py --min-coverage 80       # С минимальным покрытием 80%%")
        print("  python run_tests.py tests/test_basic.py     # Конкретный файл")
        return
    
    # Запускаем тесты
    return_code = run_tests(args)
    
    # Показываем покрытие если запрошено
    if args.coverage and args.show_html:
        show_coverage()
    
    sys.exit(return_code)


if __name__ == "__main__":
    main()