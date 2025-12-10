# core/business/ast_service.py

import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any  # Добавить Any
from core.models.code_model import CodeNode
from core.business.error_handler import handle_errors

import logging
logger = logging.getLogger('ai_code_assistant')


class ASTService:
    """
    Унифицированный сервис парсинга Python кода.
    Объединяет функционал из ast_service.py и code_tree_parser.py.
    """
    
    def __init__(self):
        self.project_tree: Dict[str, CodeNode] = {}
    
    @handle_errors(default_return={})
    def parse_project(self, directory_path: str) -> Dict[str, CodeNode]:
        """
        Парсит весь проект и возвращает дерево модулей.
        Объединяет функционал из двух исходных реализаций.
        """
        self.project_tree = {}
        
        logger.info(f"Парсинг проекта: {directory_path}")
        
        if not os.path.exists(directory_path):
            raise ValueError(f"Директория не существует: {directory_path}")
        
        python_files_found = 0
        
        # Используем Path для кроссплатформенности
        python_files = list(Path(directory_path).rglob('*.py'))
        
        for file_path in python_files:
            module_node = self.parse_module(str(file_path))
            if module_node:
                self.project_tree[str(file_path)] = module_node
                python_files_found += 1
        
        logger.info(f"Парсинг завершен: {python_files_found} файлов")
        return self.project_tree
    
    @handle_errors(default_return=None)
    def parse_module(self, file_path: str) -> Optional[CodeNode]:
        """
        Парсит один исходный .py файл в иерархию CodeNode.
        Объединяет лучшие практики из обеих реализаций.
        """
        try:
            source = Path(file_path).read_text(encoding='utf-8')
            
            try:
                tree = ast.parse(source, filename=file_path)
            except SyntaxError as e:
                logger.error(f"Синтаксическая ошибка в {file_path}: {e}")
                return self._create_error_node(file_path, source, e)
            
            module_name = Path(file_path).stem
            lines = source.split('\n')
            
            # Создаем узел модуля
            module_node = CodeNode(
                name=module_name,
                node_type='module',
                source_code=source,
                file_path=file_path
            )
            
            # Обрабатываем импорты как отдельную секцию
            import_lines = self._extract_import_section(tree, lines)
            if import_lines:
                import_node = CodeNode(
                    name='imports',
                    node_type='import_section',
                    source_code='\n'.join(import_lines),
                    file_path=file_path
                )
                module_node.add_child(import_node)
            
            # Обрабатываем классы и функции
            for item in tree.body:
                if isinstance(item, (ast.Import, ast.ImportFrom)):
                    continue  # Импорты уже обработаны
                
                elif isinstance(item, ast.ClassDef):
                    class_node = self._parse_class(item, lines, file_path)
                    module_node.add_child(class_node)
                
                elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_node = self._parse_function(item, lines, file_path)
                    module_node.add_child(func_node)
                
                else:
                    # Глобальный код можно добавить в отдельную секцию
                    pass
            
            # Добавляем секцию глобального кода
            global_code = self._extract_global_code(tree, lines)
            if global_code:
                global_node = CodeNode(
                    name='global_code',
                    node_type='global_section',
                    source_code=global_code,
                    file_path=file_path
                )
                module_node.add_child(global_node)
            
            return module_node
            
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Ошибка парсинга {file_path}: {e}")
            return None
    
    def parse_module_with_sections(self, file_path: str) -> Optional[CodeNode]:
        """
        Альтернативное имя для совместимости со старым кодом.
        Использует новую реализацию parse_module.
        """
        return self.parse_module(file_path)
    
    def _extract_import_section(self, tree: ast.AST, lines: List[str]) -> List[str]:
        """Извлекает секцию импортов"""
        import_lines = []
        
        for item in tree.body:
            if isinstance(item, (ast.Import, ast.ImportFrom)):
                start = item.lineno - 1
                end = getattr(item, 'end_lineno', start) - 1
                import_lines.extend(lines[start:end+1])
        
        return import_lines
    
    def _parse_function(self, node: ast.AST, lines: List[str], file_path: str) -> CodeNode:
        """Парсит функцию или метод"""
        start = node.lineno - 1
        end = getattr(node, 'end_lineno', start) - 1 if hasattr(node, 'end_lineno') else start
        func_src = '\n'.join(lines[start:end+1])
        
        node_type = 'function'
        if isinstance(node, ast.AsyncFunctionDef):
            node_type = 'async_function'
        
        return CodeNode(
            name=node.name,
            node_type=node_type,
            ast_node=node,
            source_code=func_src,
            file_path=file_path
        )
    
    def _parse_class(self, node: ast.ClassDef, lines: List[str], file_path: str) -> CodeNode:
        """Парсит класс с методами"""
        start = node.lineno - 1
        end = getattr(node, 'end_lineno', start) - 1 if hasattr(node, 'end_lineno') else start
        class_src = '\n'.join(lines[start:end+1])
        
        class_node = CodeNode(
            name=node.name,
            node_type='class',
            ast_node=node,
            source_code=class_src,
            file_path=file_path
        )
        
        # Методы класса
        for subitem in node.body:
            if isinstance(subitem, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_node = self._parse_function(subitem, lines, file_path)
                class_node.add_child(method_node)
        
        return class_node
    
    def _extract_global_code(self, tree: ast.AST, lines: List[str]) -> str:
        """Извлекает глобальный код (не импорты, не функции, не классы)"""
        global_lines = []
        
        for item in tree.body:
            if not isinstance(item, (ast.Import, ast.ImportFrom, 
                                   ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                start = item.lineno - 1
                end = getattr(item, 'end_lineno', start) - 1
                global_lines.extend(lines[start:end+1])
        
        return '\n'.join(global_lines) if global_lines else ""
    
    def _create_error_node(self, file_path: str, source_code: str, error: Exception) -> CodeNode:
        """Создает узел с информацией об ошибке"""
        module_name = Path(file_path).stem
        
        error_node = CodeNode(
            name=module_name,
            node_type='module_error',
            source_code=f"# Ошибка парсинга: {error}\n\n{source_code}",
            file_path=file_path
        )
        
        return error_node
    
    def find_element_in_project(self, element_name: str, element_type: str) -> Optional[CodeNode]:
        """Находит элемент в проекте по имени и типу"""
        for module_node in self.project_tree.values():
            found = self._find_element_recursive(module_node, element_name, element_type)
            if found:
                return found
        return None
    
    def _find_element_recursive(self, node: CodeNode, target_name: str, 
                               target_type: str) -> Optional[CodeNode]:
        """Рекурсивно ищет элемент в дереве"""
        if node.name == target_name and node.type == target_type:
            return node
        
        if hasattr(node, 'children'):
            for child in node.children:
                found = self._find_element_recursive(child, target_name, target_type)
                if found:
                    return found
        
        return None
    
    def get_code_preview(self, file_path: str, line_start: int, line_end: int) -> str:
        """Получает превью кода из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_start < 1 or line_end > len(lines) or line_start > line_end:
                return ""
            
            return ''.join(lines[line_start-1:line_end])
        except Exception as e:
            logger.error(f"Ошибка получения превью кода: {e}")
            return ""
    
    def get_ast_statistics(self, file_path: str) -> Dict[str, Any]:
        """Возвращает статистику по AST файла"""
        module_node = self.parse_module(file_path)
        if not module_node:
            return {}
        
        stats = {
            'classes': 0,
            'functions': 0,
            'async_functions': 0,
            'methods': 0,
            'imports': 0,
            'total_lines': len(module_node.source_code.split('\n'))
        }
        
        for child in module_node.children:
            if child.type == 'class':
                stats['classes'] += 1
                stats['methods'] += len(child.children)
            elif child.type == 'function':
                stats['functions'] += 1
            elif child.type == 'async_function':
                stats['async_functions'] += 1
            elif child.type == 'import_section':
                stats['imports'] += 1
        
        return stats