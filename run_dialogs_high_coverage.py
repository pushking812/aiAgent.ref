# run_dialogs_high_coverage.py

#!/usr/bin/env python3
"""
Скрипт для достижения высокого покрытия dialogs_view.py (85%+)
"""

import subprocess
import sys
import os
import time


def run_high_coverage_tests():
    """Запускает тесты для достижения высокого покрытия."""
    
    print("🚀 Запуск тестов для достижения 85%+ покрытия dialogs_view.py...")
    print("=" * 70)
    
    start_time = time.time()
    
    # Тестовые файлы для запуска
    test_files = [
        "tests/unit/test_dialogs_view_simple.py",
        "tests/unit/test_dialogs_view_comprehensive.py",
        "tests/unit/test_dialogs_view_lines_coverage.py",
    ]
    
    # Проверяем существование файлов
    existing_files = []
    for file in test_files:
        if os.path.exists(file):
            existing_files.append(file)
        else:
            print(f"⚠️  Файл {file} не найден")
    
    if not existing_files:
        print("❌ Нет тестовых файлов для запуска")
        return 1
    
    # Команда для запуска тестов
    cmd = [
        sys.executable, "-m", "pytest",
        *existing_files,
        "-v",
        "--tb=short",
        "--cov=gui.views.dialogs_view",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_dialogs_high",
        "--cov-fail-under=85",  # Целевое покрытие 85%
        "--disable-warnings",
        "--no-header",
        "-q"
    ]
    
    print(f"📋 Запускаем {len(existing_files)} тестовых файлов...")
    print(f"🎯 Целевое покрытие: 85%")
    print("=" * 70)
    
    # Запускаем тесты
    result = subprocess.run(cmd)
    
    elapsed_time = time.time() - start_time
    
    print("=" * 70)
    print(f"⏱️  Время выполнения: {elapsed_time:.2f} секунд")
    
    if result.returncode == 0:
        print("✅ Тесты пройдены успешно! Покрытие 85%+ достигнуто!")
    else:
        print(f"❌ Тесты завершились с ошибкой (код: {result.returncode})")
    
    # Показываем отчет о покрытии
    print("\n📊 Детальный отчет о покрытии:")
    subprocess.run([
        sys.executable, "-m", "coverage", "report",
        "--include=*/dialogs_view.py",
        "--show-missing",
        "--precision=2"
    ])
    
    # Генерируем HTML отчет
    print("\n🌐 Генерация HTML отчета...")
    subprocess.run([
        sys.executable, "-m", "coverage", "html",
        "--include=*/dialogs_view.py",
        "--directory=coverage_dialogs_html"
    ])
    
    print(f"\n📁 HTML отчет сохранен в: coverage_dialogs_html/index.html")
    
    return result.returncode


def show_current_coverage():
    """Показывает текущее покрытие."""
    print("📊 Текущее состояние покрытия dialogs_view.py:")
    print("-" * 50)
    
    cmd = [
        sys.executable, "-m", "coverage", "report",
        "--include=*/dialogs_view.py",
        "--format=total"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        coverage_value = result.stdout.strip()
        print(f"Текущее покрытие: {coverage_value}")
        
        try:
            import re
            match = re.search(r'(\d+)%', coverage_value)
            if match:
                coverage_percent = int(match.group(1))
                if coverage_percent >= 85:
                    print("✅ Цель 85% уже достигнута!")
                else:
                    print(f"🎯 Нужно еще {85 - coverage_percent}% до цели 85%")
        except:
            pass


def main():
    """Главная функция."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Запуск тестов для высокого покрытия dialogs_view.py")
    parser.add_argument("--check", action="store_true", help="Проверить текущее покрытие без запуска тестов")
    
    args = parser.parse_args()
    
    if args.check:
        show_current_coverage()
        return 0
    
    return run_high_coverage_tests()


if __name__ == "__main__":
    sys.exit(main())