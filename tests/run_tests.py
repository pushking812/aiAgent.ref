#!/usr/bin/env python3
# run_tests.py

import subprocess
import sys
import os


def run_tests():
    """Запускает все тесты."""
    print("?? Запуск тестов GUI компонентов...")
    print("=" * 60)
    
    # Определяем путь к тестам
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Команда для запуска pytest
    cmd = [
        sys.executable, '-m', 'pytest',
        tests_dir,
        '-v',
        '--cov=gui',
        '--cov-report=term',
        '--cov-report=html:coverage_html',
        '--cov-report=xml:coverage.xml'
    ]
    
    # Добавляем аргументы командной строки
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # Запускаем тесты
    print(f"Команда: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n? Все тесты пройдены успешно!")
    else:
        print("\n? Некоторые тесты не прошли")
    
    return result.returncode


def run_specific_test(test_file):
    """Запускает конкретный тестовый файл."""
    print(f"?? Запуск теста: {test_file}")
    print("=" * 60)
    
    cmd = [
        sys.executable, '-m', 'pytest',
        test_file,
        '-v'
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def show_coverage():
    """Показывает отчет о покрытии кода."""
    print("?? Отчет о покрытии кода...")
    print("=" * 60)
    
    cmd = [
        sys.executable, '-m', 'coverage',
        'report',
        '--show-missing'
    ]
    
    subprocess.run(cmd)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].endswith('.py'):
        # Запуск конкретного теста
        sys.exit(run_specific_test(sys.argv[1]))
    else:
        # Запуск всех тестов
        return_code = run_tests()
        
        if return_code == 0 and '--no-coverage' not in sys.argv:
            show_coverage()
        
        sys.exit(return_code)