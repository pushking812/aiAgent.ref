# core/business/ast_service.py

import ast
import os
from typing import Dict, List, Optional, Tuple
from core.models.code_model import CodeNode
from core.business.error_handler import handle_errors

import logging
logger = logging.getLogger('ai_code_assistant')


class ASTService:
    """Улучшенный сервис парсинга Python кода с поддержкой секционирования"""
    
    def __init__(self):
        self.project_tree: Dict[str, CodeNode] = {}
    
    @handle_errors(default_return={})
    def parse_project(self, directory_path: str) -> Dict[str, CodeNode]:
        """Парсит весь проект и возвращает дерево модулей"""
        self.project_tree = {}
        
        logger.info(f"Парсинг проекта: {directory_path}")
        
        if not os.path.exists(directory_path):
            raise ValueError(f"Директория не существует: {directory_path}")
        
        python_files_found = 0
        
        for root, dirs, files in os.walk(directory_path):
            # Игнорируем служебные директории
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_node = self.parse_module_with_sections(file_path)
                    if module_node:
                        self.project_tree[file_path] = module_node
                        python_files_found += 1
        
        logger.info(f"Парсинг завершен: {python_files_found} файлов")
        return self.project_tree
    
    @handle_errors(default_return=None)
    def parse_module_with_sections(self, file_path: str) -> Optional[CodeNode]:
        """Парсит модуль с разделением на секции (как в старом коде)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            try:
                tree = ast.parse(source_code)
            except SyntaxError as e:
                logger.error(f"Синтаксическая ошибка в {file_path}: {e}")
                return self._create_error_node(file_path, source_code, e)
            
            module_name = os.path.basename(file_path).replace('.py', '')
            
            # Создаем узел модуля
            module_node = CodeNode(
                name=module_name,
                node_type='module',
                source_code=source_code
            )
            
            lines = source_code.split('\n')
            
            # Обрабатываем импорты как отдельную секцию
            import_lines = self._extract_import_section(tree, lines)
            if import_lines:
                import_node = CodeNode(
                    name='imports',
                    node_type='import_section',
                    source_code='\n'.join(import_lines)
                )
                module_node.add_child(import_node)
            
            # Обрабатываем остальные элементы
            for item in tree.body:
                if isinstance(item, (ast.Import, ast.ImportFrom)):
                    continue  # Импорты уже обработаны
                
                elif isinstance(item, ast.ClassDef):
                    class_node = self._parse_class_with_methods(item, lines)
                    module_node.add_child(class_node)
                
                elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_node = self._parse_function(item, lines)
                    module_node.add_child(func_node)
                
                else:
                    # Глобальный код (присваивания, вызовы и т.д.)
                    # Можно добавить в отдельную секцию
                    pass
            
            # Добавляем секцию глобального кода
            global_code = self._extract_global_code(tree, lines)
            if global_code:
                global_node = CodeNode(
                    name='global_code',
                    node_type='global_section',
                    source_code=global_code
                )
                module_node.add_child(global_node)
            
            return module_node
            
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Ошибка парсинга {file_path}: {e}")
            return None
    
    def _extract_import_section(self, tree: ast.AST, lines: List[str]) -> List[str]:
        """Извлекает секцию импортов"""
        import_lines = []
        
        for item in tree.body:
            if isinstance(item, (ast.Import, ast.ImportFrom)):
                start = item.lineno - 1
                end = getattr(item, 'end_lineno', start) - 1
                import_lines.extend(lines[start:end+1])
        
        return import_lines
    
    def _parse_class_with_methods(self, class_node: ast.ClassDef, lines: List[str]) -> CodeNode:
        """Парсит класс с методами"""
        start = class_node.lineno - 1
        end = getattr(class_node, 'end_lineno', start) - 1
        class_src = '\n'.join(lines[start:end+1])
        
        node = CodeNode(
            name=class_node.name,
            node_type='class',
            source_code=class_src
        )
        
        # Добавляем методы
        for item in class_node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_node = self._parse_function(item, lines)
                node.add_child(method_node)
        
        return node
    
    def _parse_function(self, func_node: ast.AST, lines: List[str]) -> CodeNode:
        """Парсит функцию или метод"""
        start = func_node.lineno - 1
        end = getattr(func_node, 'end_lineno', start) - 1
        func_src = '\n'.join(lines[start:end+1])
        
        node_type = 'function'
        if isinstance(func_node, ast.AsyncFunctionDef):
            node_type = 'async_function'
        elif hasattr(func_node, '_is_method') and func_node._is_method:
            node_type = 'method'
        
        return CodeNode(
            name=func_node.name,
            node_type=node_type,
            source_code=func_src
        )
    
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
        module_name = os.path.basename(file_path).replace('.py', '')
        
        error_node = CodeNode(
            name=module_name,
            node_type='module_error',
            source_code=f"# Ошибка парсинга: {error}\n\n{source_code}"
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