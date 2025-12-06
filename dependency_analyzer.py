#!/usr/bin/env python3
"""
Скрипт для визуализации зависимостей между Python-модулями.
Требуется установка: pip install graphviz pydot
"""

import os
import ast
import sys
from pathlib import Path
from collections import defaultdict
import subprocess
from typing import Dict, List, Set, Tuple

try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

class ModuleDependencyAnalyzer:
    def __init__(self, root_dir: str, exclude_dirs: List[str] = None):
        """
        Инициализация анализатора зависимостей.
        
        Args:
            root_dir: Корневая директория проекта
            exclude_dirs: Директории для исключения
        """
        self.root_dir = Path(root_dir).absolute()
        self.exclude_dirs = set(exclude_dirs or [])
        self.exclude_dirs.update(['venv', '.venv', 'env', '.env', '__pycache__', '.git'])
        
        # Хранение данных о зависимостях
        self.modules: Dict[str, Path] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        
    def find_python_modules(self) -> None:
        """Находит все Python-модули в проекте."""
        for py_file in self.root_dir.rglob("*.py"):
            # Пропускаем исключенные директории
            if any(excluded in py_file.parts for excluded in self.exclude_dirs):
                continue
                
            # Получаем имя модуля
            rel_path = py_file.relative_to(self.root_dir)
            module_name = self.path_to_module_name(rel_path)
            
            self.modules[module_name] = py_file
            
    def path_to_module_name(self, path: Path) -> str:
        """Преобразует путь в имя модуля."""
        # Убираем расширение .py
        if path.name == '__init__.py':
            module_path = path.parent
            return str(module_path).replace(os.sep, '.')
        else:
            module_path = path.with_suffix('')
            return str(module_path).replace(os.sep, '.')
    
    def extract_imports(self, file_path: Path) -> Set[str]:
        """Извлекает все импорты из файла."""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Обработка import module
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Берем только первый компонент (основное имя модуля)
                        module_name = alias.name.split('.')[0]
                        imports.add(module_name)
                
                # Обработка from module import ...
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # может быть None для относительных импортов
                        module_name = node.module.split('.')[0]
                        imports.add(module_name)
                        
        except (SyntaxError, UnicodeDecodeError):
            print(f"Warning: Не удалось проанализировать файл {file_path}")
            
        return imports
    
    def analyze_dependencies(self) -> None:
        """Анализирует зависимости между модулями."""
        print(f"Анализ зависимостей в {self.root_dir}...")
        
        # Сначала находим все модули
        self.find_python_modules()
        print(f"Найдено модулей: {len(self.modules)}")
        
        # Анализируем зависимости для каждого модуля
        for module_name, file_path in self.modules.items():
            imports = self.extract_imports(file_path)
            
            # Фильтруем только те импорты, которые есть в нашем проекте
            for imported in imports:
                # Проверяем, является ли это внутренним модулем
                for project_module in self.modules.keys():
                    # Простая проверка: модуль начинается с имени импорта
                    if imported == project_module.split('.')[0]:
                        if imported != module_name.split('.')[0]:  # исключаем самоподключения
                            self.dependencies[module_name].add(imported)
    
    def create_dependency_graph(self, output_format: str = 'png',
                               show_external: bool = False) -> None:
        """
        Создает визуальный граф зависимостей.
        
        Args:
            output_format: Формат вывода ('png', 'svg', 'pdf', 'dot')
            show_external: Показывать внешние зависимости
        """
        if not HAS_GRAPHVIZ:
            print("Установите graphviz: pip install graphviz")
            return
        
        # Создаем граф
        dot = graphviz.Digraph(comment='Module Dependencies',
                              format=output_format,
                              graph_attr={'rankdir': 'LR', 'splines': 'ortho'})
        
        # Добавляем узлы (модули)
        for module in sorted(self.modules.keys()):
            # Разные стили для пакетов и модулей
            if module.endswith('.__init__'):
                # Это пакет
                label = module.replace('.__init__', '')
                dot.node(module, label=label, shape='folder',
                        style='filled', fillcolor='lightblue')
            else:
                # Обычный модуль
                label = module
                dot.node(module, label=label, shape='box',
                        style='filled', fillcolor='lightyellow')
        
        # Добавляем зависимости
        for source, targets in self.dependencies.items():
            for target in targets:
                # Находим полное имя целевого модуля
                full_target = None
                for mod in self.modules.keys():
                    if mod == target or mod.startswith(target + '.'):
                        full_target = mod
                        break
                
                if full_target:
                    dot.edge(source, full_target)
        
        # Внешние зависимости (если нужно)
        if show_external:
            external_deps = set()
            for module_name, file_path in self.modules.items():
                all_imports = self.extract_imports(file_path)
                for imp in all_imports:
                    if imp not in self.modules:
                        external_deps.add(imp)
            
            for ext in sorted(external_deps):
                dot.node(ext, label=ext, shape='ellipse',
                        style='filled', fillcolor='lightgrey')
        
        # Сохраняем граф
        output_file = 'module_dependencies'
        dot.render(output_file, cleanup=True)
        print(f"Граф сохранен как {output_file}.{output_format}")
        
    def create_text_report(self) -> None:
        """Создает текстовый отчет о зависимостях."""
        print("\n" + "="*60)
        print("ОТЧЕТ О ЗАВИСИМОСТЯХ МОДУЛЕЙ")
        print("="*60)
        
        # Группируем по пакетам
        packages = defaultdict(list)
        for module in self.modules.keys():
            package = module.split('.')[0]
            packages[package].append(module)
        
        for package, modules in sorted(packages.items()):
            print(f"\n📦 {package}:")
            for module in sorted(modules):
                deps = self.dependencies.get(module, [])
                if deps:
                    print(f"  ├── {module}")
                    for dep in sorted(deps):
                        print(f"  │   └── → {dep}")
                else:
                    print(f"  └── {module} (нет зависимостей)")
        
        # Статистика
        print("\n" + "="*60)
        print("СТАТИСТИКА:")
        print(f"Всего модулей: {len(self.modules)}")
        
        modules_with_deps = sum(1 for deps in self.dependencies.values() if deps)
        print(f"Модулей с зависимостями: {modules_with_deps}")
        
        total_deps = sum(len(deps) for deps in self.dependencies.values())
        print(f"Всего зависимостей: {total_deps}")
        
        # Поиск циклических зависимостей
        cycles = self.find_cycles()
        if cycles:
            print(f"\n⚠️  Обнаружены циклические зависимости:")
            for cycle in cycles[:3]:  # Показываем только первые 3
                print(f"  {' → '.join(cycle)}")
            if len(cycles) > 3:
                print(f"  ... и еще {len(cycles) - 3} циклов")
    
    def find_cycles(self) -> List[List[str]]:
        """Находит циклические зависимости в графе."""
        visited = set()
        stack = []
        cycles = []
        
        def dfs(node, path):
            visited.add(node)
            stack.append(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor in stack:
                    # Найден цикл
                    start_idx = stack.index(neighbor)
                    cycle = stack[start_idx:] + [neighbor]
                    cycles.append(cycle.copy())
                elif neighbor not in visited:
                    dfs(neighbor, path + [neighbor])
            
            stack.pop()
        
        for node in self.modules.keys():
            if node not in visited:
                dfs(node, [])
        
        return cycles

def main():
    """Основная функция."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Анализатор зависимостей Python-модулей'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Путь к корневой директории проекта (по умолчанию: текущая директория)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['png', 'svg', 'pdf', 'dot'],
        default='png',
        help='Формат выходного файла (по умолчанию: png)'
    )
    parser.add_argument(
        '-e', '--external',
        action='store_true',
        help='Показывать внешние зависимости'
    )
    parser.add_argument(
        '-t', '--text',
        action='store_true',
        help='Только текстовый отчет (без графики)'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Дополнительные директории для исключения'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование директории
    if not os.path.exists(args.path):
        print(f"Ошибка: Директория '{args.path}' не существует")
        sys.exit(1)
    
    # Создаем анализатор
    analyzer = ModuleDependencyAnalyzer(args.path, exclude_dirs=args.exclude)
    
    try:
        # Анализируем зависимости
        analyzer.analyze_dependencies()
        
        # Создаем текстовый отчет
        analyzer.create_text_report()
        
        # Создаем визуализацию (если не указан флаг --text)
        if not args.text and HAS_GRAPHVIZ:
            analyzer.create_dependency_graph(
                output_format=args.format,
                show_external=args.external
            )
        elif not args.text and not HAS_GRAPHVIZ:
            print("\nДля создания графического графа установите:")
            print("1. Graphviz: https://graphviz.org/download/")
            print("2. Python библиотеку: pip install graphviz")
            
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()