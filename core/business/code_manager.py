# core/business/code_manager.py

import ast
import re
from typing import Dict, List, Tuple, Optional
from core.models.code_model import CodeNode
from .ast_service import ASTService
from .change_service import CodeChange, PendingChange, ChangeManager
from .error_handler import handle_errors

import logging
logger = logging.getLogger('ai_code_assistant')


class CodeManager:
    """Управляет интеграцией AI-кода в проект"""
    
    def __init__(self):
        self.ast_service = ASTService()
        self.change_manager = ChangeManager()
    
    @handle_errors(default_return=[])
    def analyze_ai_code(self, ai_code: str, project_tree: Dict[str, CodeNode], 
                       target_file_path: str = "") -> List[CodeChange]:
        """Анализирует AI-код и возвращает список изменений"""
        changes = []
        
        logger.info(f"Анализ AI-кода: {len(ai_code)} символов")
        
        try:
            ai_tree = ast.parse(ai_code)
            ai_entities = self._extract_entities(ai_tree, ai_code)
            
            for entity_name, entity_type, entity_code in ai_entities:
                change = self._analyze_entity(
                    entity_name, entity_type, entity_code, 
                    project_tree, target_file_path
                )
                if change:
                    changes.append(change)
                    
            logger.info(f"Анализ завершен: {len(changes)} изменений")
            
        except SyntaxError as e:
            logger.error(f"Синтаксическая ошибка в AI-коде: {e}")
            error_change = CodeChange(
                action='conflict',
                entity_name='AI Code',
                new_code=ai_code,
                file_path=target_file_path,
                node_type='error'
            )
            error_change.conflict_reason = f"Синтаксическая ошибка: {e}"
            changes.append(error_change)
        
        return changes
    
    def _extract_entities(self, tree: ast.AST, source_code: str) -> List[Tuple[str, str, str]]:
        """Извлекает сущности из AST дерева"""
        entities = []
        
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                node_type = 'function'
                if isinstance(node, ast.ClassDef):
                    node_type = 'class'
                elif isinstance(node, ast.AsyncFunctionDef):
                    node_type = 'async_function'
                
                entity_code = ast.get_source_segment(source_code, node)
                if entity_code:
                    entities.append((node.name, node_type, entity_code))
        
        return entities
    
    def _analyze_entity(self, entity_name: str, entity_type: str, entity_code: str,
                       project_tree: Dict[str, CodeNode], target_file_path: str) -> Optional[CodeChange]:
        """Анализирует одну сущность и определяет необходимое действие"""
        
        # Ищем существующую сущность
        existing_entity = self._find_entity_in_project(entity_name, entity_type, project_tree)
        
        if existing_entity:
            # Проверяем конфликты
            has_conflict, conflict_details = self._check_for_conflicts(existing_entity, entity_code)
            
            if has_conflict:
                change = CodeChange(
                    action='conflict',
                    entity_name=entity_name,
                    new_code=entity_code,
                    old_code=existing_entity.source_code,
                    file_path=target_file_path,
                    node_type=entity_type
                )
                change.conflict_reason = "Обнаружены различия в сигнатуре или реализации"
                return change
            else:
                # Замена без конфликтов
                return CodeChange(
                    action='replace',
                    entity_name=entity_name,
                    new_code=entity_code,
                    old_code=existing_entity.source_code,
                    file_path=target_file_path,
                    node_type=entity_type
                )
        else:
            # Новая сущность
            return CodeChange(
                action='add',
                entity_name=entity_name,
                new_code=entity_code,
                file_path=target_file_path,
                node_type=entity_type
            )
    
    def _find_entity_in_project(self, entity_name: str, entity_type: str, 
                               project_tree: Dict[str, CodeNode]) -> Optional[CodeNode]:
        """Ищет сущность в проекте по имени и типу"""
        for module_node in project_tree.values():
            found = self._find_entity_recursive(module_node, entity_name, entity_type)
            if found:
                return found
        return None
    
    def _find_entity_recursive(self, node: CodeNode, target_name: str, target_type: str) -> Optional[CodeNode]:
        """Рекурсивно ищет сущность в дереве"""
        if node.name == target_name and node.type == target_type:
            return node
        
        for child in node.children:
            found = self._find_entity_recursive(child, target_name, target_type)
            if found:
                return found
        
        return None
    
    def _check_for_conflicts(self, existing_entity: CodeNode, new_code: str) -> Tuple[bool, str]:
        """Проверяет наличие конфликтов"""
        old_code = existing_entity.source_code.strip()
        new_code_clean = new_code.strip()
        
        # Если коды идентичны - нет конфликта
        if old_code == new_code_clean:
            return False, ""
        
        try:
            old_ast = ast.parse(old_code)
            new_ast = ast.parse(new_code_clean)
            
            if len(old_ast.body) > 0 and len(new_ast.body) > 0:
                old_node = old_ast.body[0]
                new_node = new_ast.body[0]
                
                if isinstance(old_node, (ast.FunctionDef, ast.AsyncFunctionDef)) and \
                   isinstance(new_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return self._compare_functions(old_node, new_node), "сигнатура функции"
                
                elif isinstance(old_node, ast.ClassDef) and isinstance(new_node, ast.ClassDef):
                    return self._compare_classes(old_node, new_node), "сигнатура класса"
            
            return True, "тело функции/класса"
            
        except SyntaxError:
            return self._heuristic_compare(old_code, new_code_clean), "эвристическое сравнение"
    
    def _compare_functions(self, old_func: ast.FunctionDef, new_func: ast.FunctionDef) -> bool:
        """Сравнивает две функции на предмет конфликтов"""
        if old_func.name != new_func.name:
            return True
        
        old_args = self._get_args_count(old_func.args)
        new_args = self._get_args_count(new_func.args)
        
        return old_args != new_args
    
    def _compare_classes(self, old_class: ast.ClassDef, new_class: ast.ClassDef) -> bool:
        """Сравнивает два класса на предмет конфликтов"""
        return old_class.name != new_class.name
    
    def _get_args_count(self, args: ast.arguments) -> int:
        """Подсчитывает количество аргументов функции"""
        count = len(args.args) + len(args.kwonlyargs)
        if args.vararg:
            count += 1
        if args.kwarg:
            count += 1
        return count
    
    def _heuristic_compare(self, old_code: str, new_code: str) -> bool:
        """Эвристическое сравнение кода"""
        old_clean = self._remove_comments_and_spaces(old_code)
        new_clean = self._remove_comments_and_spaces(new_code)
        
        return old_clean != new_clean
    
    def _remove_comments_and_spaces(self, code: str) -> str:
        """Удаляет комментарии и лишние пробелы из кода"""
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def get_change_manager(self) -> ChangeManager:
        """Возвращает менеджер изменений"""
        return self.change_manager