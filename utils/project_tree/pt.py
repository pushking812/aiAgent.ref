#!/usr/bin/env python3
"""
Скрипт для построения полного дерева проекта Python.
Формат: папка.модуль.класс.метод
"""

import os
import ast
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional, Any
import argparse

class ProjectTreeBuilder:
    def __init__(self, root_path: str, exclude_patterns: List[str] = None):
        """
        Инициализация построителя дерева проекта.
        
        Args:
            root_path: Корневой путь проекта
            exclude_patterns: Паттерны для исключения
        """
        self.root_path = Path(root_path).absolute()
        self.exclude_patterns = exclude_patterns or []
        self.exclude_patterns.extend([
            'venv', '.venv', '__pycache__', '.git', '.idea', 
            '.vscode', 'node_modules', '*.pyc', '*.pyo', '__pycache__'
        ])
        
        # Структура дерева
        self.tree = {
            'name': self.root_path.name,
            'type': 'project',
            'path': str(self.root_path),
            'children': []
        }
        
        # Статистика
        self.stats = {
            'packages': 0,
            'modules': 0,
            'classes': 0,
            'methods': 0,
            'functions': 0
        }
    
    def should_exclude(self, path: Path) -> bool:
        """Проверяет, нужно ли исключить путь."""
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                # Проверка по расширению
                if str(path).endswith(pattern[1:]):
                    return True
            elif pattern in path.parts:
                return True
        return False
    
    def build_tree(self) -> None:
        """Строит полное дерево проекта."""
        print(f"?? Построение дерева проекта: {self.root_path}")
        
        # Сначала строим файловую структуру
        self._build_file_structure()
        
        # Затем анализируем содержимое файлов
        self._analyze_file_contents()
        
        print(f"? Дерево построено. Статистика: {self.stats}")
    
    def _build_file_structure(self) -> None:
        """Строит файловую структуру проекта."""
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            
            # Фильтруем исключенные директории
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]
            
            # Получаем относительный путь от корня проекта
            rel_path = root_path.relative_to(self.root_path)
            
            # Создаем путь в дереве
            current_node = self.tree
            if rel_path != Path('.'):
                for part in rel_path.parts:
                    # Ищем существующую директорию
                    found = False
                    for child in current_node['children']:
                        if child['name'] == part and child['type'] == 'directory':
                            current_node = child
                            found = True
                            break
                    
                    # Создаем новую директорию, если не найдена
                    if not found:
                        new_dir = {
                            'name': part,
                            'type': 'directory',
                            'path': str(self.root_path / rel_path),
                            'children': []
                        }
                        current_node['children'].append(new_dir)
                        current_node = new_dir
            
            # Добавляем Python файлы
            py_files = [f for f in files if f.endswith('.py') 
                       and not self.should_exclude(root_path / f)]
            
            for py_file in py_files:
                module_node = {
                    'name': py_file,
                    'type': 'module',
                    'path': str(root_path / py_file),
                    'classes': [],
                    'functions': [],
                    'children': []
                }
                current_node['children'].append(module_node)
                self.stats['modules'] += 1
    
    def _analyze_file_contents(self) -> None:
        """Анализирует содержимое Python файлов."""
        def analyze_node(node):
            if node['type'] == 'directory':
                for child in node['children']:
                    analyze_node(child)
            elif node['type'] == 'module':
                self._analyze_module(node)
        
        analyze_node(self.tree)
    
    def _analyze_module(self, module_node: Dict) -> None:
        """Анализирует один Python модуль."""
        file_path = Path(module_node['path'])
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Собираем информацию о классе
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node)
                    module_node['classes'].append(class_info)
                    self.stats['classes'] += 1
                
                elif isinstance(node, ast.FunctionDef):
                    # Проверяем, не является ли это методом класса
                    # (методы уже обработаны в analyze_class)
                    if not self._is_method(node):
                        func_info = self._analyze_function(node)
                        module_node['functions'].append(func_info)
                        self.stats['functions'] += 1
                        
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"??  Ошибка при анализе {file_path}: {e}")
    
    def _analyze_class(self, class_node: ast.ClassDef) -> Dict:
        """Анализирует класс и его методы."""
        class_info = {
            'name': class_node.name,
            'type': 'class',
            'bases': [],
            'methods': [],
            'attributes': [],
            'docstring': ast.get_docstring(class_node)
        }
        
        # Базовые классы
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                class_info['bases'].append(base.id)
        
        # Методы и атрибуты
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_info = self._analyze_method(node)
                class_info['methods'].append(method_info)
                self.stats['methods'] += 1
            elif isinstance(node, ast.AnnAssign) or isinstance(node, ast.Assign):
                # Атрибуты класса
                attr_info = self._analyze_attribute(node)
                if attr_info:
                    class_info['attributes'].append(attr_info)
        
        return class_info
    
    def _analyze_method(self, method_node: ast.FunctionDef) -> Dict:
        """Анализирует метод класса."""
        method_info = {
            'name': method_node.name,
            'type': 'method',
            'args': [],
            'decorators': [],
            'docstring': ast.get_docstring(method_node),
            'is_async': isinstance(method_node, ast.AsyncFunctionDef)
        }
        
        # Аргументы
        args = method_node.args
        if args.args:
            for arg in args.args:
                method_info['args'].append(arg.arg)
        
        # Декораторы
        for decorator in method_node.decorator_list:
            if isinstance(decorator, ast.Name):
                method_info['decorators'].append(decorator.id)
        
        return method_info
    
    def _analyze_function(self, func_node: ast.FunctionDef) -> Dict:
        """Анализирует функцию уровня модуля."""
        func_info = {
            'name': func_node.name,
            'type': 'function',
            'args': [],
            'decorators': [],
            'docstring': ast.get_docstring(func_node),
            'is_async': isinstance(func_node, ast.AsyncFunctionDef)
        }
        
        # Аргументы
        args = func_node.args
        if args.args:
            for arg in args.args:
                func_info['args'].append(arg.arg)
        
        # Декораторы
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name):
                func_info['decorators'].append(decorator.id)
        
        return func_info
    
    def _analyze_attribute(self, attr_node: ast.AST) -> Optional[Dict]:
        """Анализирует атрибут класса."""
        if isinstance(attr_node, ast.AnnAssign):
            # Аннотированное присваивание: name: type = value
            if isinstance(attr_node.target, ast.Name):
                return {
                    'name': attr_node.target.id,
                    'type': 'attribute',
                    'annotation': self._get_annotation(attr_node.annotation)
                }
        elif isinstance(attr_node, ast.Assign):
            # Обычное присваивание
            for target in attr_node.targets:
                if isinstance(target, ast.Name):
                    return {
                        'name': target.id,
                        'type': 'attribute'
                    }
        return None
    
    def _get_annotation(self, annotation: Optional[ast.AST]) -> str:
        """Получает строковое представление аннотации типа."""
        if annotation is None:
            return ''
        elif isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            # Обработка типа List[str] и т.д.
            return ast.unparse(annotation)
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        return ''
    
    def _is_method(self, func_node: ast.FunctionDef) -> bool:
        """Проверяет, является ли функция методом класса."""
        # Простая проверка: если у функции есть аргумент self/cls, то это метод
        args = func_node.args.args
        if args and args[0].arg in ('self', 'cls'):
            return True
        return False
    
    def print_tree(self, max_depth: int = 10, show_docstrings: bool = False) -> None:
        """Печатает дерево в консоли."""
        print("\n" + "="*80)
        print(f"?? ДЕРЕВО ПРОЕКТА: {self.root_path.name}")
        print("="*80)
        self._print_node(self.tree, 0, max_depth, show_docstrings)
        print("\n" + "="*80)
        self._print_statistics()
    
    def _print_node(self, node: Dict, level: int, max_depth: int, 
                   show_docstrings: bool) -> None:
        """Рекурсивно печатает узел дерева."""
        if level > max_depth:
            return
        
        indent = "    " * level
        prefix = "¦   " * (level - 1) if level > 0 else ""
        
        # Определяем иконку в зависимости от типа
        icons = {
            'project': '??',
            'directory': '??',
            'module': '??',
            'class': '??',
            'method': '??',
            'function': '??',
            'attribute': '??'
        }
        
        icon = icons.get(node['type'], '?')
        
        if node['type'] == 'project':
            print(f"{icon} {node['name']}")
        elif node['type'] == 'directory':
            print(f"{prefix}+-- {icon} {node['name']}/")
        elif node['type'] == 'module':
            print(f"{prefix}+-- {icon} {node['name']}")
            
            # Показываем классы и функции модуля
            if level + 1 <= max_depth:
                # Классы
                for class_info in node.get('classes', []):
                    class_indent = "¦   " * level
                    print(f"{class_indent}+-- ?? {class_info['name']}")
                    
                    # Методы класса
                    if level + 2 <= max_depth:
                        for method in class_info.get('methods', []):
                            method_indent = "¦   " * (level + 1)
                            decorators = ""
                            if method.get('decorators'):
                                decorators = f" [@{', @'.join(method['decorators'])}]"
                            async_prefix = "async " if method.get('is_async') else ""
                            args_str = f"({', '.join(method['args'])})" if method.get('args') else "()"
                            
                            print(f"{method_indent}+-- ??  {async_prefix}{method['name']}{args_str}{decorators}")
                            
                            # Докстринг метода
                            if show_docstrings and method.get('docstring'):
                                doc_indent = "¦   " * (level + 2)
                                doc_preview = method['docstring'][:50] + "..." \
                                            if len(method['docstring']) > 50 else method['docstring']
                                print(f"{doc_indent}+-- ?? \"{doc_preview}\"")
                    
                    # Атрибуты класса
                    if level + 2 <= max_depth:
                        for attr in class_info.get('attributes', []):
                            attr_indent = "¦   " * (level + 1)
                            annotation = f": {attr['annotation']}" if attr.get('annotation') else ""
                            print(f"{attr_indent}+-- ?? {attr['name']}{annotation}")
                
                # Функции уровня модуля
                for func in node.get('functions', []):
                    func_indent = "¦   " * level
                    decorators = ""
                    if func.get('decorators'):
                        decorators = f" [@{', @'.join(func['decorators'])}]"
                    async_prefix = "async " if func.get('is_async') else ""
                    args_str = f"({', '.join(func['args'])})" if func.get('args') else "()"
                    
                    print(f"{func_indent}+-- ?? {async_prefix}{func['name']}{args_str}{decorators}")
        
        # Рекурсивно обрабатываем дочерние узлы
        if node['type'] in ['project', 'directory']:
            for child in node.get('children', []):
                self._print_node(child, level + 1, max_depth, show_docstrings)
    
    def _print_statistics(self) -> None:
        """Печатает статистику проекта."""
        print("?? СТАТИСТИКА ПРОЕКТА:")
        print(f"   Пакетов/директорий: {self.stats['packages']}")
        print(f"   Модулей: {self.stats['modules']}")
        print(f"   Классов: {self.stats['classes']}")
        print(f"   Методов: {self.stats['methods']}")
        print(f"   Функций: {self.stats['functions']}")
        print(f"   Всего элементов: {sum(self.stats.values())}")
    
    def export_to_text(self, output_file: str = "project_tree.txt") -> None:
        """Экспортирует дерево в текстовый файл."""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Сохраняем оригинальный stdout
            original_stdout = sys.stdout
            sys.stdout = f
            
            try:
                self.print_tree(max_depth=10, show_docstrings=True)
            finally:
                sys.stdout = original_stdout
        
        print(f"?? Дерево экспортировано в {output_file}")
    
    def export_to_json(self, output_file: str = "project_structure.json") -> None:
        """Экспортирует структуру в JSON."""
        import json
        
        def serialize_node(node):
            """Сериализует узел для JSON."""
            result = {
                'name': node['name'],
                'type': node['type'],
                'path': node.get('path', '')
            }
            
            if node['type'] == 'module':
                result['classes'] = node.get('classes', [])
                result['functions'] = node.get('functions', [])
            
            if 'children' in node:
                result['children'] = [serialize_node(child) for child in node['children']]
            
            return result
        
        structure = {
            'project': self.root_path.name,
            'root_path': str(self.root_path),
            'stats': self.stats,
            'tree': serialize_node(self.tree)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"?? Структура экспортирована в JSON: {output_file}")
    
    def find_element(self, search_term: str) -> List[Dict]:
        """Находит элемент по имени в дереве."""
        results = []
        
        def search_node(node, path=""):
            current_path = f"{path}.{node['name']}" if path else node['name']
            
            # Проверяем совпадение
            if search_term.lower() in node['name'].lower():
                results.append({
                    'path': current_path,
                    'type': node['type'],
                    'full_path': node.get('path', '')
                })
            
            # Ищем в содержимом модуля
            if node['type'] == 'module':
                for class_info in node.get('classes', []):
                    class_path = f"{current_path}.{class_info['name']}"
                    if search_term.lower() in class_info['name'].lower():
                        results.append({
                            'path': class_path,
                            'type': 'class',
                            'full_path': node['path']
                        })
                    
                    for method in class_info.get('methods', []):
                        method_path = f"{class_path}.{method['name']}"
                        if search_term.lower() in method['name'].lower():
                            results.append({
                                'path': method_path,
                                'type': 'method',
                                'full_path': node['path']
                            })
            
            # Рекурсивный поиск в дочерних узлах
            for child in node.get('children', []):
                search_node(child, current_path)
        
        search_node(self.tree)
        return results

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description='Построитель дерева проекта Python (папка.модуль.класс.метод)'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Путь к проекту (по умолчанию: текущая директория)'
    )
    parser.add_argument(
        '-d', '--depth',
        type=int,
        default=4,
        help='Максимальная глубина отображения (по умолчанию: 4)'
    )
    parser.add_argument(
        '--docstrings',
        action='store_true',
        help='Показывать докстринги'
    )
    parser.add_argument(
        '-t', '--text',
        action='store_true',
        help='Экспортировать в текстовый файл'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Экспортировать в JSON'
    )
    parser.add_argument(
        '-s', '--search',
        help='Поиск элемента по имени'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Дополнительные паттерны для исключения'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование пути
    if not os.path.exists(args.path):
        print(f"? Ошибка: путь '{args.path}' не существует")
        sys.exit(1)
    
    # Создаем построитель дерева
    builder = ProjectTreeBuilder(args.path, exclude_patterns=args.exclude)
    
    try:
        # Строим дерево
        builder.build_tree()
        
        # Поиск элемента
        if args.search:
            results = builder.find_element(args.search)
            if results:
                print(f"\n?? Результаты поиска '{args.search}':")
                for result in results:
                    type_icons = {
                        'directory': '??',
                        'module': '??',
                        'class': '??',
                        'method': '??',
                        'function': '??'
                    }
                    icon = type_icons.get(result['type'], '?')
                    print(f"   {icon} {result['path']} ({result['type']})")
            else:
                print(f"\n?? По запросу '{args.search}' ничего не найдено")
        
        # Показываем дерево в консоли
        builder.print_tree(max_depth=args.depth, show_docstrings=args.docstrings)
        
        # Экспорт в текстовый файл
        if args.text:
            builder.export_to_text()
        
        # Экспорт в JSON
        if args.json:
            builder.export_to_json()
        
    except KeyboardInterrupt:
        print("\n\n??  Прервано пользователем")
    except Exception as e:
        print(f"\n? Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()