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
        
        if args.min_coverage:
            cmd.extend([f"--cov-fail-under={args.min_coverage}"])
    
    # Фильтр для пропуска проблемных тестов
    if args.skip_problematic:
        cmd.extend(["-k", "not test_modified_status_visual_feedback and not test_treeview_initialization and not test_matches_dot_notation_logic"])
    
    # Добавляем конкретные тесты если указаны
    if args.test_files:
        cmd.extend(args.test_files)
    
    print(f"🚀 Запуск тестов...")
    print(f"📋 Команда: {' '.join(cmd[:5])}...")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ Все тесты пройдены успешно!")
    else:
        print(f"❌ Тесты завершились с ошибкой (код: {result.returncode})")
    
    return result.returncode


def show_coverage():
    """Показывает отчет о покрытии."""
    cmd = [sys.executable, "-m", "coverage", "report", "--show-missing", "--omit=*test*"]
    
    print(f"\n📊 Отчет о покрытии кода:")
    print("=" * 60)
    
    subprocess.run(cmd)


def show_quick_coverage():
    """Быстрая проверка покрытия."""
    if not os.path.exists(".coverage"):
        print("ℹ️ Файл .coverage не найден. Сначала запустите тесты с опцией --coverage")
        return
    
    cmd = [sys.executable, "-m", "coverage", "report", "--format=total", "--omit=*test*"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        coverage_value = result.stdout.strip()
        print(f"📊 Текущее покрытие: {coverage_value}")
        
        try:
            # Пытаемся извлечь числовое значение
            import re
            match = re.search(r'(\d+)%', coverage_value)
            if match:
                coverage_percent = int(match.group(1))
                if coverage_percent >= 75:
                    print(f"✅ Цель 75% достигнута!")
                else:
                    print(f"⚠️  Нужно еще {75 - coverage_percent}% до цели 75%")
        except:
            pass


def run_specific_module_tests(module_name):
    """Запускает тесты для конкретного модуля."""
    test_files = {
        'dialogs': ['tests/test_dialogs_final.py', 'tests/test_dialogs_simple.py'],
        'main_window': ['tests/test_main_window_view.py'],
        'code_editor': ['tests/test_code_editor_view.py'],
        'project_tree': ['tests/test_project_tree_view.py'],
        'integration': ['tests/test_integration.py'],
        'basic': ['tests/test_basic.py'],
        'all_gui': [
            'tests/test_main_window_view.py',
            'tests/test_code_editor_view.py',
            'tests/test_project_tree_view.py',
            'tests/test_dialogs_final.py',
            'tests/test_integration.py'
        ]
    }
    
    if module_name not in test_files:
        print(f"❌ Неизвестный модуль: {module_name}")
        print(f"   Доступные модули: {', '.join(test_files.keys())}")
        return 1
    
    print(f"🎯 Запуск тестов для модуля: {module_name}")
    print("=" * 60)
    
    cmd = [sys.executable, "-m", "pytest", *test_files[module_name], "-v", "--tb=short", "--disable-warnings"]
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    return result.returncode


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
        default=75,
        help="Минимальный процент покрытия (по умолчанию: 75%%)"
    )
    
    parser.add_argument(
        "--module",
        choices=['dialogs', 'main_window', 'code_editor', 'project_tree', 
                'integration', 'basic', 'all_gui'],
        help="Запустить тесты для конкретного модуля"
    )
    
    parser.add_argument(
        "--check-coverage",
        action="store_true",
        help="Проверить текущее покрытие без запуска тестов"
    )
    
    parser.add_argument(
        "--skip-problematic",
        action="store_true",
        help="Пропустить проблемные тесты с Tkinter сравнениями"
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
        print("  python run_tests.py --module dialogs        # Только тесты dialogs")
        print("  python run_tests.py --module all_gui        # Все GUI тесты")
        print("  python run_tests.py --check-coverage        # Проверить текущее покрытие")
        print("  python run_tests.py --skip-problematic      # Пропустить проблемные тесты")
        print("  python run_tests.py --min-coverage 80       # С минимальным покрытием 80%%")
        print("  python run_tests.py tests/test_basic.py     # Конкретный файл")
        return 0
    
    # Проверка покрытия без запуска тестов
    if args.check_coverage:
        show_quick_coverage()
        return 0
    
    # Запуск тестов для конкретного модуля
    if args.module:
        return run_specific_module_tests(args.module)
    
    # Запуск обычных тестов
    return_code = run_tests(args)
    
    # Показываем покрытие если запрошено
    if args.coverage and return_code == 0:
        show_coverage()
    
    sys.exit(return_code)


if __name__ == "__main__":
    main()