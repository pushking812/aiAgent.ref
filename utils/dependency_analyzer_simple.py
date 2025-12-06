#!/usr/bin/env python3
"""
Упрощенный анализатор зависимостей без внешних зависимостей.
"""

import os
import ast
from pathlib import Path
from collections import defaultdict

def analyze_project_dependencies(root_path="."):
    """
    Анализирует зависимости в Python проекте.
    
    Args:
        root_path: Путь к корневой директории проекта
    """
    root = Path(root_path).absolute()
    
    # Находим все Python файлы
    python_files = list(root.rglob("*.py"))
    
    # Исключаем виртуальные окружения и кэши
    python_files = [
        f for f in python_files 
        if not any(part in str(f) for part in ['venv', '.venv', '__pycache__'])
    ]
    
    print(f"Найдено {len(python_files)} Python файлов")
    
    # Словарь для хранения зависимостей
    dependencies = defaultdict(set)
    module_paths = {}
    
    # Собираем информацию о модулях
    for file_path in python_files:
        # Преобразуем путь в имя модуля
        rel_path = file_path.relative_to(root)
        if file_path.name == '__init__.py':
            module_name = str(rel_path.parent).replace(os.sep, '.')
        else:
            module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')
        
        module_paths[module_name] = file_path
        
        # Извлекаем импорты
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep = alias.name.split('.')[0]
                        if dep in module_paths and dep != module_name.split('.')[0]:
                            dependencies[module_name].add(dep)
                            
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep = node.module.split('.')[0]
                        if dep in module_paths and dep != module_name.split('.')[0]:
                            dependencies[module_name].add(dep)
                            
        except Exception as e:
            print(f"Ошибка при анализе {file_path}: {e}")
    
    # Выводим результат
    print("\n" + "="*50)
    print("ЗАВИСИМОСТИ МОДУЛЕЙ:")
    print("="*50)
    
    # Группируем по первому уровню
    level1 = defaultdict(list)
    for module in module_paths:
        first_part = module.split('.')[0]
        level1[first_part].append(module)
    
    for package, modules in sorted(level1.items()):
        print(f"\n📁 {package.upper()}")
        for module in sorted(modules):
            deps = dependencies.get(module, [])
            if deps:
                print(f"  ├─ {module}")
                for dep in sorted(deps):
                    print(f"  │   └─→ {dep}")
            else:
                print(f"  └─ {module}")
    
    # Статистика
    print("\n" + "="*50)
    print("СТАТИСТИКА:")
    print(f"Всего модулей: {len(module_paths)}")
    
    modules_with_deps = sum(1 for deps in dependencies.values() if deps)
    print(f"Модулей с зависимостями: {modules_with_deps}")
    
    total_deps = sum(len(deps) for deps in dependencies.values())
    print(f"Всего связей: {total_deps}")

if __name__ == "__main__":
    import sys
    
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    analyze_project_dependencies(path)