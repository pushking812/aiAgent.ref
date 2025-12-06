# run_tests.py

import subprocess
import sys
import os
import argparse


def run_tests(args):
    """Запускает тесты с указанными параметрами."""
    cmd = [sys.executable, "-m", "pytest", "tests/"]  # Всегда начинаем с tests/
    
    # Если указаны конкретные тестовые файлы, добавляем их (вместо tests/)
    if args.test_files:
        cmd = [sys.executable, "-m", "pytest"] + args.test_files
    
    # Добавляем общие опции
    cmd.extend(["-v", "--tb=short", "--disable-warnings"])
    
    # Добавляем пользовательские опции
    if args.marker:
        cmd.extend(["-m", args.marker])
    
    if args.runslow:
        cmd.append("--runslow")
    
    if args.coverage:
        cmd.extend([
            "--cov=gui",
            "--cov-report=term",
            "--cov-report=html:coverage_html"
        ])
        
        if args.min_coverage:
            cmd.extend([f"--cov-fail-under={args.min_coverage}"])
    
    print(f"🚀 Запуск тестов...")
    print(f"📋 Команда: {' '.join(cmd[:10])}{'...' if len(cmd) > 10 else ''}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ Все тесты пройдены успешно!")
    else:
        print(f"❌ Тесты завершились с ошибкой (код: {result.returncode})")
    
    return result.returncode

def run_dialogs_coverage_tests():
    """Запускает тесты для увеличения покрытия dialogs_view.py до 85%+."""
    print("🎯 Запуск тестов для достижения 85%+ покрытия dialogs_view.py...")
    
    cmd = [sys.executable, "run_dialogs_high_coverage.py"]
    result = subprocess.run(cmd)
    
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
                if coverage_percent >= 70:
                    print(f"✅ Цель 70% достигнута!")
                else:
                    print(f"⚠️  Нужно еще {70 - coverage_percent}% до цели 70%")
        except:
            pass


def run_specific_module_tests(module_name):
    """Запускает тесты для конкретного модуля."""
    test_files = {
        'unit': ['tests/unit/'],
        'gui': ['tests/gui/'],
        'integration': ['tests/integration/'],
        'main_window': ['tests/unit/test_main_window_view.py'],
        'code_editor': ['tests/unit/test_code_editor_view.py'],
        'project_tree': ['tests/unit/test_project_tree_view.py'],
        'dialogs': ['tests/unit/test_dialogs_view.py'],
        'all_gui': ['tests/unit/', 'tests/gui/'],
        'all': ['tests/unit/', 'tests/gui/', 'tests/integration/']
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


def run_tests_with_gui():
    """Запускает GUI тесты с поддержкой headless режима."""
    import platform
    
    print("🖥️  Запуск GUI тестов...")
    
    if platform.system() == "Linux":
        print("🐧 Linux: запускаем с xvfb-run")
        cmd = ["xvfb-run", "--auto-servernum", "--server-args=-screen 0 1024x768x24",
               sys.executable, "-m", "pytest", "tests/gui/", "-v", "--tb=short", "--run-gui"]
    else:
        print(f"💻 {platform.system()}: запускаем напрямую")
        cmd = [sys.executable, "-m", "pytest", "tests/gui/", "-v", "--tb=short", "--run-gui"]
    
    print(f"📋 Команда: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    
    print("=" * 60)
    return result.returncode


def run_dialogs_coverage_tests():
    """Запускает тесты для увеличения покрытия dialogs_view.py."""
    print("🎯 Запуск тестов для увеличения покрытия dialogs_view.py...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/test_dialogs_view_coverage_fixed.py",
        "tests/unit/test_dialogs_view_direct_coverage.py",
        "-v",
        "--tb=short",
        "--cov=gui.views.dialogs_view",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_dialogs",
        "--disable-warnings"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Тесты пройдены успешно!")
        
        # Показываем отчет о покрытии
        print("\n📊 Отчет о покрытии dialogs_view.py:")
        subprocess.run([
            sys.executable, "-m", "coverage", "report",
            "--include=*/dialogs_view.py",
            "--show-missing"
        ])
    else:
        print(f"❌ Тесты завершились с ошибкой (код: {result.returncode})")
    
    return result.returncode


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Запуск тестов GUI приложения")
    
    parser.add_argument(
        "-m", "--marker",
        help="Запустить тесты с указанным маркером (gui, unit, integration, tkinter, slow)"
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
        default=70,
        help="Минимальный процент покрытия (по умолчанию: 70%%)"
    )
    
    parser.add_argument(
        "--module",
        choices=['unit', 'gui', 'integration', 'main_window', 'code_editor', 
                'project_tree', 'dialogs', 'all_gui', 'all'],
        help="Запустить тесты для конкретного модуля"
    )
    
    parser.add_argument(
        "--check-coverage",
        action="store_true",
        help="Проверить текущее покрытие без запуска тестов"
    )
    
    parser.add_argument(
        "--gui-headless",
        action="store_true",
        help="Запустить GUI тесты в headless режиме (только Linux)"
    )
    
    parser.add_argument(
        "--dialogs-coverage",
        action="store_true",
        help="Запустить тесты для увеличения покрытия dialogs_view.py"
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
        print("  python run_tests.py -m gui                  # GUI тесты")
        print("  python run_tests.py -m unit                 # Только unit тесты")
        print("  python run_tests.py --module dialogs        # Только тесты диалогов")
        print("  python run_tests.py --module all_gui        # Все GUI тесты")
        print("  python run_tests.py --module all            # Все тесты")
        print("  python run_tests.py --check-coverage        # Проверить текущее покрытие")
        print("  python run_tests.py --runslow              # Включая медленные тесты")
        print("  python run_tests.py --min-coverage 80      # С минимальным покрытием 80%%")
        print("  python run_tests.py --gui-headless         # GUI тесты в headless режиме")
        print("  python run_tests.py --dialogs-coverage     # Увеличить покрытие dialogs_view.py")
        print("  python run_tests.py tests/unit/            # Тесты из директории")
        print("  python run_tests.py tests/unit/test_basic.py    # Конкретный файл")
        return 0
    
    # Проверка покрытия без запуска тестов
    if args.check_coverage:
        show_quick_coverage()
        return 0
    
    # Запуск GUI тестов в headless режиме
    if args.gui_headless:
        return run_tests_with_gui()
    
    # Запуск тестов для увеличения покрытия dialogs_view.py
    if args.dialogs_coverage:
        return run_dialogs_coverage_tests()
    
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