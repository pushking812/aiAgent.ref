#!/usr/bin/env python3
"""
Версия с улучшенным форматированием и дополнительной информацией.
"""

import ast
from pathlib import Path
import os

class DetailedProjectTree:
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.tree = {}
        
    def build_detailed_tree(self):
        """Строит детализированное дерево проекта."""
        print(f"\n{'='*100}")
        print(f"ДЕТАЛИЗИРОВАННОЕ ДЕРЕВО ПРОЕКТА: {self.root.name}")
        print(f"{'='*100}\n")
        
        for py_file in self.root.rglob("*.py"):
            # Пропускаем исключенные
            if any(x in str(py_file) for x in ['venv', '__pycache__', '.git']):
                continue
            
            # Получаем относительный путь
            rel_path = py_file.relative_to(self.root)
            path_parts = list(rel_path.parts)
            
            # Форматируем вывод
            self._print_file_structure(py_file, path_parts)
    
    def _print_file_structure(self, file_path: Path, path_parts: list):
        """Печатает структуру файла в формате папка.модуль.класс.метод."""
        
        # Печатаем путь к файлу
        indent = "  " * (len(path_parts) - 1)
        
        if path_parts[-1] == '__init__.py':
            # Это пакет
            package_name = '.'.join(path_parts[:-1]) or self.root.name
            print(f"{indent}📦 {package_name}")
        else:
            # Это модуль
            module_name = '.'.join(path_parts)
            module_name = module_name.replace('.py', '')
            print(f"{indent}📄 {module_name}")
            
            # Анализируем содержимое модуля
            self._analyze_module_content(file_path, indent + "  ")
    
    def _analyze_module_content(self, file_path: Path, indent: str):
        """Анализирует и печатает содержимое модуля."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Собираем все элементы
            elements = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node)
                    elements.append(('class', class_info))
                    
                    # Добавляем методы класса
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = self._extract_method_info(item)
                            elements.append(('method', method_info))
                
                elif isinstance(node, ast.FunctionDef):
                    # Проверяем, не является ли это методом класса
                    if not self._is_method(node):
                        func_info = self._extract_function_info(node)
                        elements.append(('function', func_info))
            
            # Печатаем элементы
            for elem_type, elem_info in elements:
                if elem_type == 'class':
                    print(f"{indent}└── 🎯 {elem_info['name']}")
                    
                    # Печатаем методы этого класса
                    for method in elem_info.get('methods', []):
                        print(f"{indent}    └── ⚙️  {method}")
                
                elif elem_type == 'method':
                    # Методы уже обработаны в разделе классов
                    pass
                
                elif elem_type == 'function':
                    print(f"{indent}└── 🔧 {elem_info['name']}")
                        
        except Exception as e:
            print(f"{indent}⚠️  Ошибка анализа: {e}")
    
    def _extract_class_info(self, class_node: ast.ClassDef) -> dict:
        """Извлекает информацию о классе."""
        info = {
            'name': class_node.name,
            'methods': [],
            'bases': [],
            'docstring': ast.get_docstring(class_node)
        }
        
        # Базовые классы
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                info['bases'].append(base.id)
        
        # Методы
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_name = node.name
                decorators = []
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(f"@{decorator.id}")
                
                method_str = method_name
                if decorators:
                    method_str += f" {' '.join(decorators)}"
                
                info['methods'].append(method_str)
        
        return info
    
    def _extract_method_info(self, method_node: ast.FunctionDef) -> dict:
        """Извлекает информацию о методе."""
        return {
            'name': method_node.name,
            'args': [arg.arg for arg in method_node.args.args],
            'decorators': [decorator.id for decorator in method_node.decorator_list 
                          if isinstance(decorator, ast.Name)]
        }
    
    def _extract_function_info(self, func_node: ast.FunctionDef) -> dict:
        """Извлекает информацию о функции."""
        return {
            'name': func_node.name,
            'args': [arg.arg for arg in func_node.args.args],
            'decorators': [decorator.id for decorator in func_node.decorator_list 
                          if isinstance(decorator, ast.Name)]
        }
    
    def _is_method(self, func_node: ast.FunctionDef) -> bool:
        """Проверяет, является ли функция методом класса."""
        if func_node.args.args:
            first_arg = func_node.args.args[0].arg
            return first_arg in ('self', 'cls')
        return False

def print_project_summary(root_path):
    """Печатает сводку проекта."""
    print(f"\n{'='*60}")
    print("КРАТКАЯ СВОДКА ПРОЕКТА")
    print(f"{'='*60}")
    
    root = Path(root_path)
    
    # Собираем статистику
    packages = []
    modules = []
    classes = []
    functions = []
    
    for py_file in root.rglob("*.py"):
        if any(x in str(py_file) for x in ['venv', '__pycache__', '.git']):
            continue
        
        rel_path = py_file.relative_to(root)
        
        if py_file.name == '__init__.py':
            packages.append('.'.join(rel_path.parts[:-1]) or root.name)
        else:
            modules.append('.'.join(rel_path.parts).replace('.py', ''))
            
            # Анализируем содержимое
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append(f"{'.'.join(rel_path.parts).replace('.py', '')}.{node.name}")
                    elif isinstance(node, ast.FunctionDef):
                        # Проверяем, не метод ли это
                        if not (node.args.args and node.args.args[0].arg in ('self', 'cls')):
                            functions.append(f"{'.'.join(rel_path.parts).replace('.py', '')}.{node.name}")
                            
            except:
                pass
    
    # Выводим статистику
    print(f"\n📦 Пакеты ({len(packages)}):")
    for pkg in sorted(packages)[:10]:  # Показываем первые 10
        print(f"   - {pkg}")
    if len(packages) > 10:
        print(f"   ... и еще {len(packages) - 10} пакетов")
    
    print(f"\n📄 Модули ({len(modules)}):")
    for mod in sorted(modules)[:10]:
        print(f"   - {mod}")
    if len(modules) > 10:
        print(f"   ... и еще {len(modules) - 10} модулей")
    
    print(f"\n🎯 Классы ({len(classes)}):")
    for cls in sorted(classes)[:10]:
        print(f"   - {cls}")
    if len(classes) > 10:
        print(f"   ... и еще {len(classes) - 10} классов")
    
    print(f"\n🔧 Функции ({len(functions)}):")
    for func in sorted(functions)[:10]:
        print(f"   - {func}")
    if len(functions) > 10:
        print(f"   ... и еще {len(functions) - 10} функций")
    
    print(f"\n📊 Всего элементов: {len(packages) + len(modules) + len(classes) + len(functions)}")

if __name__ == "__main__":
    import sys
    
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Создаем детализированное дерево
    tree = DetailedProjectTree(path)
    tree.build_detailed_tree()
    
    # Печатаем сводку
    print_project_summary(path)