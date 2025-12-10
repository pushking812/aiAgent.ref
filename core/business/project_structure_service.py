# core/business/project_structure_service.py

"""
Сервис для получения полной структуры проекта с AST анализом.
Объединяет данные из репозитория и AST сервиса.
"""

import os
import logging
from typing import Dict, Any
from core.data.project_repository import ProjectRepository
from core.business.ast_service import ASTService
from core.business.error_handler import handle_errors

logger = logging.getLogger('ai_code_assistant')


class ProjectStructureService:
    """Сервис для получения полной структуры проекта."""
    
    def __init__(self, project_repository: ProjectRepository = None, ast_service: ASTService = None):
        self.project_repository = project_repository or ProjectRepository()
        self.ast_service = ast_service or ASTService()
        logger.debug("Инициализирован ProjectStructureService")
    
    @handle_errors(default_return={})
    def get_full_project_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Возвращает полную структуру проекта с AST анализом.
        
        Args:
            project_path: Путь к проекту
            
        Returns:
            Dict с полной структурой проекта
        """
        logger.info(f"Получение полной структуры проекта: {project_path}")
        
        # Открываем проект в репозитории
        if not self.project_repository.open(project_path):
            logger.error(f"Не удалось открыть проект: {project_path}")
            return {}
        
        # Получаем файловую структуру
        file_structure = self.project_repository.get_project_structure()
        if not file_structure:
            logger.error(f"Пустая файловая структура для проекта: {project_path}")
            return {}
        
        # Добавляем путь проекта
        file_structure['project_path'] = project_path
        
        try:
            # Парсим AST структуру
            ast_tree = self.ast_service.parse_project(project_path)
            file_structure['ast_tree'] = ast_tree
            
            # Обогащаем файлы AST данными
            self._enrich_files_with_ast(file_structure, ast_tree)
            
            # Добавляем статистику
            file_structure['statistics'] = self._calculate_statistics(file_structure, ast_tree)
            
            logger.info(f"Полная структура проекта получена: "
                       f"{len(file_structure.get('files', {}))} файлов, "
                       f"{len(ast_tree)} модулей с AST")
            
            return file_structure
            
        except Exception as e:
            logger.error(f"Ошибка при анализе AST структуры: {e}")
            # Возвращаем хотя бы файловую структуру
            return file_structure
    
    def _enrich_files_with_ast(self, file_structure: Dict[str, Any], ast_tree: Dict[str, Any]):
        """Обогащает информацию о файлах AST данными."""
        files = file_structure.get('files', {})
        
        for file_path, ast_node in ast_tree.items():
            # Получаем относительный путь
            rel_path = os.path.relpath(file_path, file_structure['project_path'])
            
            if rel_path in files:
                if isinstance(files[rel_path], dict):
                    files[rel_path]['ast_node'] = ast_node
                else:
                    # Если файл хранится как строка, преобразуем в словарь
                    files[rel_path] = {
                        'content': files[rel_path],
                        'ast_node': ast_node,
                        'path': file_path,
                        'module': files[rel_path].get('module', '') if isinstance(files[rel_path], dict) else ''
                    }
            else:
                # Файл есть в AST, но нет в базовой структуре
                # Может быть скрытый или новый файл
                module_path = os.path.dirname(rel_path)
                module_name = module_path.replace(os.sep, '.') if module_path != '.' else ''
                
                files[rel_path] = {
                    'content': ast_node.source_code if hasattr(ast_node, 'source_code') else '',
                    'ast_node': ast_node,
                    'path': file_path,
                    'module': module_name,
                    'name': os.path.basename(file_path)
                }
                
                # Добавляем модуль если нужно
                if module_name and module_name not in file_structure.get('modules', []):
                    file_structure.setdefault('modules', []).append(module_name)
    
    def _calculate_statistics(self, file_structure: Dict[str, Any], ast_tree: Dict[str, Any]) -> Dict[str, Any]:
        """Вычисляет статистику по проекту."""
        stats = {
            'total_files': len(file_structure.get('files', {})),
            'python_files': len(ast_tree),
            'directories': len(file_structure.get('directories', [])),
            'modules': len(file_structure.get('modules', [])),
            'classes': 0,
            'functions': 0,
            'methods': 0,
            'import_sections': 0,
            'errors': 0
        }
        
        # Подсчитываем элементы из AST
        for ast_node in ast_tree.values():
            if ast_node.type == 'module_error':
                stats['errors'] += 1
                continue
                
            for child in ast_node.children:
                if child.type == 'class':
                    stats['classes'] += 1
                    stats['methods'] += len([c for c in child.children if c.type == 'method'])
                elif child.type in ['function', 'async_function']:
                    stats['functions'] += 1
                elif child.type == 'import_section':
                    stats['import_sections'] += 1
        
        return stats
    
    @handle_errors(default_return={})
    def get_file_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Возвращает только файловую структуру проекта (без AST).
        Быстрее, чем полная структура.
        """
        if not self.project_repository.open(project_path):
            return {}
        
        structure = self.project_repository.get_project_structure()
        structure['project_path'] = project_path
        return structure
    
    @handle_errors(default_return={})
    def get_ast_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Возвращает только AST структуру проекта.
        """
        try:
            return self.ast_service.parse_project(project_path)
        except Exception as e:
            logger.error(f"Ошибка получения AST структуры: {e}")
            return {}
    
    def get_file_with_ast(self, file_path: str, project_path: str = None) -> Dict[str, Any]:
        """
        Возвращает информацию о файле с его AST структурой.
        """
        try:
            # Получаем содержимое файла
            content = self.project_repository.read_file(file_path)
            
            # Парсим AST
            ast_node = self.ast_service.parse_module(file_path)
            
            return {
                'path': file_path,
                'content': content,
                'ast_node': ast_node,
                'module': self._get_module_name(file_path, project_path),
                'name': os.path.basename(file_path)
            }
        except Exception as e:
            logger.error(f"Ошибка получения файла с AST: {e}")
            return {}
    
    def _get_module_name(self, file_path: str, project_path: str = None) -> str:
        """Возвращает имя модуля для файла."""
        if project_path and file_path.startswith(project_path):
            rel_path = os.path.relpath(os.path.dirname(file_path), project_path)
            if rel_path == '.':
                return ''
            return rel_path.replace(os.sep, '.')
        return ''