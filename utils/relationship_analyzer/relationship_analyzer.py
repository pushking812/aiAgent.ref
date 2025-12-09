# relationship_analyzer.py

"""
Скрипт для визуализации как графа зависимостей, так и дерева отношений Python-модулей.
Добавлен функционал построения иерархического дерева.
"""

import os
import ast
import sys
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Any
import argparse

try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

class FullRelationshipAnalyzer:
    def __init__(self, root_dir: str, exclude_dirs: List[str] = None):
        self.root_dir = Path(root_dir).absolute()
        self.exclude_dirs = set(exclude_dirs or [])
        self.exclude_dirs.update(['venv', '.venv', 'env', '.env', '__pycache__', '.git', '.idea', 'node_modules'])
        
        # Данные о модулях
        self.modules: Dict[str, Path] = {}
        self.package_structure: Dict[str, List[str]] = defaultdict(list)
        
        # Различные типы отношений
        self.import_relations: Dict[str, Set[str]] = defaultdict(set)  # импорты
        self.inheritance_relations: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)  # наследование
        self.function_calls: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)  # вызовы функций
        self.class_composition: Dict[str, Set[str]] = defaultdict(set)  # композиция классов
        
    def analyze_project(self) -> None:
        """Полный анализ проекта."""
        print(f"🔍 Анализ проекта: {self.root_dir}")
        
        # 1. Находим все модули
        self._find_all_modules()
        print(f"   Найдено модулей: {len(self.modules)}")
        
        # 2. Строим структуру пакетов
        self._build_package_structure()
        
        # 3. Анализируем каждый модуль
        for module_name, file_path in self.modules.items():
            self._analyze_module(module_name, file_path)
        
        # 4. Анализируем наследование между модулями
        self._analyze_cross_module_inheritance()
        
    def _find_all_modules(self) -> None:
        """Находит все Python-модули в проекте."""
        for py_file in self.root_dir.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in self.exclude_dirs):
                continue
                
            rel_path = py_file.relative_to(self.root_dir)
            module_name = self._path_to_module_name(rel_path)
            self.modules[module_name] = py_file
    
    def _path_to_module_name(self, path: Path) -> str:
        """Преобразует путь в имя модуля."""
        if path.name == '__init__.py':
            module_path = path.parent
            return str(module_path).replace(os.sep, '.')
        else:
            module_path = path.with_suffix('')
            return str(module_path).replace(os.sep, '.')
    
    def _build_package_structure(self) -> None:
        """Строит иерархическую структуру пакетов."""
        for module_name in self.modules.keys():
            parts = module_name.split('.')
            for i in range(1, len(parts) + 1):
                parent = '.'.join(parts[:i])
                if i < len(parts):
                    child = '.'.join(parts[:i+1])
                    if child not in self.package_structure[parent]:
                        self.package_structure[parent].append(child)
    
    def _analyze_module(self, module_name: str, file_path: Path) -> None:
        """Анализирует один модуль."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Извлекаем импорты
            self._extract_imports(module_name, tree)
            
            # Извлекаем информацию о классах и наследовании
            self._extract_classes(module_name, tree)
            
            # Извлекаем вызовы функций
            self._extract_function_calls(module_name, tree)
            
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"⚠️  Ошибка анализа {module_name}: {e}")
    
    def _extract_imports(self, module_name: str, tree: ast.AST) -> None:
        """Извлекает импорты из модуля."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name.split('.')[0]
                    if imported in self.modules and imported != module_name.split('.')[0]:
                        self.import_relations[module_name].add(imported)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported = node.module.split('.')[0]
                    if imported in self.modules and imported != module_name.split('.')[0]:
                        self.import_relations[module_name].add(imported)
    
    def _extract_classes(self, module_name: str, tree: ast.AST) -> None:
        """Извлекает информацию о классах и наследовании."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                full_class_name = f"{module_name}.{class_name}"
                
                # Анализ базовых классов
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_name = base.id
                        # Проверяем, определен ли базовый класс в этом же модуле
                        self.inheritance_relations[module_name].add((class_name, base_name))
    
    def _extract_function_calls(self, module_name: str, tree: ast.AST) -> None:
        """Извлекает вызовы функций."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    function_name = node.func.id
                    # Запоминаем, что в этом модуле вызывается функция с таким именем
                    self.function_calls[module_name].add(("function_call", function_name))
    
    def _analyze_cross_module_inheritance(self) -> None:
        """Анализирует наследование между классами из разных модулей."""
        # Эта упрощенная версия показывает только наследование внутри модулей
        # Для кросс-модульного наследования нужен более сложный анализ
        pass
    
    def create_full_tree(self, output_file: str = "project_tree") -> None:
        """
        Создает полное дерево отношений проекта.
        Включает иерархию пакетов, модули и основные отношения.
        """
        if not HAS_GRAPHVIZ:
            print("Установите graphviz: pip install graphviz")
            return
        
        # Создаем граф для дерева
        dot = graphviz.Digraph(
            name='Project Full Tree',
            format='png',
            graph_attr={
                'rankdir': 'TB',  # Top to Bottom для дерева
                'splines': 'ortho',
                'nodesep': '0.8',
                'ranksep': '1.0'
            },
            node_attr={
                'fontname': 'Helvetica',
                'fontsize': '10'
            }
        )
        
        # Строим дерево пакетов и модулей
        self._add_tree_nodes(dot)
        
        # Добавляем зависимости между модулями
        self._add_dependency_edges(dot)
        
        # Добавляем наследование
        self._add_inheritance_edges(dot)
        
        # Сохраняем
        dot.render(output_file, cleanup=True)
        print(f"🌳 Полное дерево проекта сохранено как {output_file}.png")
    
    def _add_tree_nodes(self, dot: graphviz.Digraph) -> None:
        """Добавляет узлы дерева (пакеты и модули)."""
        visited = set()
        
        def add_node(name: str, level: int):
            if name in visited:
                return
            visited.add(name)
            
            # Определяем тип узла
            if name in self.modules:
                # Это модуль
                label = name.split('.')[-1] if '.' in name else name
                if self._is_package(name):
                    # Пакет (есть подмодули)
                    dot.node(name, label=label, shape='folder', 
                            style='filled', fillcolor='lightblue',
                            tooltip=f"Package: {name}")
                else:
                    # Обычный модуль
                    dot.node(name, label=label, shape='box',
                            style='filled', fillcolor='lightyellow',
                            tooltip=f"Module: {name}")
            else:
                # Вспомогательный узел для структуры
                label = name.split('.')[-1] if '.' in name else name
                dot.node(name, label=label, shape='ellipse',
                        style='dashed', fillcolor='white',
                        tooltip=f"Namespace: {name}")
            
            # Рекурсивно добавляем дочерние узлы
            if name in self.package_structure:
                for child in sorted(self.package_structure[name]):
                    add_node(child, level + 1)
                    # Добавляем ребро для иерархии
                    dot.edge(name, child, style='solid', color='black', arrowhead='none')
        
        # Начинаем с корневых пакетов
        root_packages = [p for p in self.package_structure.keys() 
                        if '.' not in p or p.split('.')[0] == p]
        
        for root in sorted(set([p.split('.')[0] for p in self.modules.keys()])):
            add_node(root, 0)
    
    def _is_package(self, module_name: str) -> bool:
        """Проверяет, является ли модуль пакетом (имеет подмодули)."""
        return module_name in self.package_structure and len(self.package_structure[module_name]) > 0
    
    def _add_dependency_edges(self, dot: graphviz.Digraph) -> None:
        """Добавляет ребра зависимостей между модулями."""
        for source, targets in self.import_relations.items():
            for target in targets:
                # Находим полное имя целевого модуля
                full_target = None
                for mod in self.modules.keys():
                    if mod == target or mod.startswith(target + '.'):
                        full_target = mod
                        break
                
                if full_target and source != full_target:
                    dot.edge(source, full_target, 
                            color='blue', style='solid',
                            arrowhead='normal', label='imports',
                            fontsize='8', fontcolor='blue')
    
    def _add_inheritance_edges(self, dot: graphviz.Digraph) -> None:
        """Добавляет ребра наследования."""
        for module, inherits in self.inheritance_relations.items():
            for child, parent in inherits:
                # Создаем имена узлов для классов
                child_node = f"{module}.{child}"
                parent_node = f"{module}.{parent}"
                
                dot.node(child_node, label=child, shape='box',
                        style='filled', fillcolor='lightgreen')
                dot.node(parent_node, label=parent, shape='box',
                        style='filled', fillcolor='lightcoral')
                
                dot.edge(child_node, parent_node,
                        color='green', style='dashed',
                        arrowhead='onormal', label='inherits',
                        fontsize='8', fontcolor='green')
    
    def create_hierarchical_tree_text(self) -> None:
        """Создает текстовое представление иерархического дерева."""
        print("\n" + "="*70)
        print("🌳 ПОЛНОЕ ДЕРЕВО ОТНОШЕНИЙ ПРОЕКТА")
        print("="*70)
        
        # Группируем модули по первому уровню
        root_level = defaultdict(list)
        for module in self.modules.keys():
            first_part = module.split('.')[0]
            root_level[first_part].append(module)
        
        for root, modules in sorted(root_level.items()):
            print(f"\n📦 {root.upper()}/")
            self._print_subtree(root, modules, indent=2)
        
        # Выводим статистику отношений
        self._print_relationship_statistics()
    
    def _print_subtree(self, parent: str, all_modules: List[str], indent: int = 0) -> None:
        """Рекурсивно печатает поддерево."""
        # Находим непосредственных детей
        children = []
        for module in all_modules:
            if module.startswith(parent + '.') and '.' in module[len(parent)+1:]:
                next_part = module[len(parent)+1:].split('.')[0]
                child_name = f"{parent}.{next_part}"
                if child_name not in children:
                    children.append(child_name)
            elif module == parent:
                # Это сам родительский модуль
                pass
        
        # Сортируем детей
        children.sort()
        
        # Печатаем детей
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            prefix = "    " * indent + ("└── " if is_last else "├── ")
            
            # Определяем, является ли ребенок пакетом
            child_modules = [m for m in all_modules if m.startswith(child + '.') or m == child]
            
            if len(child_modules) > 1 or any('.' in m[len(child)+1:] for m in child_modules if m != child):
                # Это пакет
                print(f"{prefix}📁 {child.split('.')[-1]}/")
                self._print_subtree(child, all_modules, indent + 1)
            else:
                # Это модуль
                module_name = child.split('.')[-1]
                
                # Собираем информацию о модуле
                deps = self.import_relations.get(child, [])
                inherits = self.inheritance_relations.get(child, [])
                
                dep_str = f" [imports: {len(deps)}]" if deps else ""
                inherit_str = f" [inherits: {len(inherits)}]" if inherits else ""
                
                print(f"{prefix}📄 {module_name}.py{dep_str}{inherit_str}")
                
                # Показываем зависимости этого модуля
                if deps and indent < 3:  # Ограничиваем вложенность
                    for j, dep in enumerate(sorted(deps)[:3]):  # Показываем первые 3
                        dep_prefix = "    " * (indent + 1) + ("└── " if (j == len(deps[:3])-1 and len(deps) <= 3) else "├── ")
                        print(f"{dep_prefix}→ {dep}")
                    if len(deps) > 3:
                        print(f"{'    ' * (indent + 1)}└── ... и еще {len(deps) - 3}")
    
    def _print_relationship_statistics(self) -> None:
        """Печатает статистику отношений."""
        print("\n" + "="*70)
        print("📊 СТАТИСТИКА ОТНОШЕНИЙ")
        print("="*70)
        
        total_imports = sum(len(deps) for deps in self.import_relations.values())
        total_inheritance = sum(len(inherits) for inherits in self.inheritance_relations.values())
        
        print(f"Всего модулей: {len(self.modules)}")
        print(f"Модулей с импортами: {len(self.import_relations)}")
        print(f"Всего импортов: {total_imports}")
        print(f"Модулей с наследованием: {len(self.inheritance_relations)}")
        print(f"Всего отношений наследования: {total_inheritance}")
        
        # Находим наиболее связанные модули
        if self.import_relations:
            most_dependent = max(self.import_relations.items(), 
                               key=lambda x: len(x[1]), 
                               default=(None, set()))
            most_imported = defaultdict(int)
            for deps in self.import_relations.values():
                for dep in deps:
                    most_imported[dep] += 1
            
            if most_imported:
                most_popular = max(most_imported.items(), key=lambda x: x[1])
                print(f"\n🎯 Наиболее зависимый модуль: {most_dependent[0]} "
                      f"({len(most_dependent[1])} импортов)")
                print(f"🎯 Наиболее импортируемый модуль: {most_popular[0]} "
                      f"({most_popular[1]} ссылок)")
        
        # Анализ циклических зависимостей
        cycles = self._find_cycles()
        if cycles:
            print(f"\n⚠️  Обнаружено циклических зависимостей: {len(cycles)}")
            for i, cycle in enumerate(cycles[:2], 1):
                print(f"  Цикл {i}: {' → '.join(cycle)}")
    
    def _find_cycles(self) -> List[List[str]]:
        """Находит циклические зависимости."""
        visited = set()
        stack = []
        cycles = []
        
        def dfs(node):
            visited.add(node)
            stack.append(node)
            
            for neighbor in self.import_relations.get(node, []):
                # Находим полное имя соседа
                full_neighbor = None
                for mod in self.modules.keys():
                    if mod == neighbor or mod.startswith(neighbor + '.'):
                        full_neighbor = mod
                        break
                
                if full_neighbor:
                    if full_neighbor in stack:
                        # Найден цикл
                        start_idx = stack.index(full_neighbor)
                        cycle = stack[start_idx:] + [full_neighbor]
                        cycles.append(cycle.copy())
                    elif full_neighbor not in visited:
                        dfs(full_neighbor)
            
            stack.pop()
        
        for node in self.modules.keys():
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def export_to_json(self, output_file: str = "project_structure.json") -> None:
        """Экспортирует структуру проекта в JSON."""
        import json
        
        structure = {
            "project_root": str(self.root_dir),
            "modules": list(self.modules.keys()),
            "package_structure": dict(self.package_structure),
            "import_relations": {
                k: list(v) for k, v in self.import_relations.items()
            },
            "inheritance_relations": {
                k: [f"{child}→{parent}" for child, parent in v]
                for k, v in self.inheritance_relations.items()
            },
            "statistics": {
                "total_modules": len(self.modules),
                "modules_with_imports": len(self.import_relations),
                "total_imports": sum(len(deps) for deps in self.import_relations.values()),
                "modules_with_inheritance": len(self.inheritance_relations),
                "total_inheritance": sum(len(inherits) for inherits in self.inheritance_relations.values())
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Данные экспортированы в {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Анализатор полного дерева отношений Python-проекта'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Путь к проекту'
    )
    parser.add_argument(
        '-t', '--tree',
        action='store_true',
        help='Построить иерархическое дерево'
    )
    parser.add_argument(
        '-g', '--graph',
        action='store_true',
        help='Построить граф зависимостей'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Экспортировать в JSON'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['png', 'svg', 'pdf'],
        default='png',
        help='Формат графического вывода'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Директории для исключения'
    )
    
    args = parser.parse_args()
    
    # Создаем анализатор
    analyzer = FullRelationshipAnalyzer(args.path, exclude_dirs=args.exclude)
    
    try:
        # Выполняем анализ
        analyzer.analyze_project()
        
        # Строим дерево (текстовое)
        if args.tree:
            analyzer.create_hierarchical_tree_text()
        
        # Строим графическое дерево
        if args.graph and HAS_GRAPHVIZ:
            analyzer.create_full_tree(f"project_tree_{args.format}")
        elif args.graph and not HAS_GRAPHVIZ:
            print("\nДля графического вывода установите graphviz")
            print("pip install graphviz")
            print("Или используйте только текстовый вывод с флагом -t")
        
        # Экспортируем в JSON
        if args.json:
            analyzer.export_to_json()
        
        # Если не указаны флаги, показываем краткую справку
        if not any([args.tree, args.graph, args.json]):
            print("\nИспользуйте флаги для вывода:")
            print("  -t, --tree     : Текстовое дерево отношений")
            print("  -g, --graph    : Графическое дерево (требует graphviz)")
            print("  -j, --json     : Экспорт в JSON")
            print("\nПример: python script.py /path/to/project -t -g")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()