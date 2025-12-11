# templates/python_basic/main.py

"""
{project_name} - Основной модуль приложения
"""

import os
import sys


def main():
    """Основная функция приложения"""
    print(f"Запуск приложения {project_name}")
    
    try:
        # TODO: Добавить логику приложения
        print("Приложение запущено!")
        
    except Exception as e:
        print(f"Ошибка при выполнении приложения: {e}")
        raise
    
    print("Приложение завершено")


if __name__ == "__main__":
    main()