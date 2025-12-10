# core/business/project_creator_service.py

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from .error_handler import handle_errors
from .ai_schema_service import AISchemaService

import logging
logger = logging.getLogger('ai_code_assistant')


class ProjectCreatorService:
    """Сервис создания проектов из AI-схем и шаблонов"""
    
    def __init__(self):
        logger.debug("Инициализирован ProjectCreatorService")
    
    @handle_errors(default_return=False)
    def create_project_from_ai_schema(self, schema: Dict[str, Any], project_path: str) -> bool:
        """Создает проект на основе схемы от AI"""
        logger.info(f"Создание проекта из AI схемы: {project_path}")
        
        try:
            project_dir = Path(project_path)
            if not self._create_directory(project_dir):
                return False
            
            # Создаем директории
            self._create_directories_structure(project_dir, schema.get('modules', []))
            
            # Создаем файлы
            self._create_files(project_dir, schema.get('files', {}))
            
            logger.info(f"Проект успешно создан: {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при создании проекта: {e}")
            return False
    
    @handle_errors(default_return=False)
    def create_basic_python_project(self, project_path: str, project_name: str) -> bool:
        """Создает базовую структуру Python проекта"""
        logger.info(f"Создание базового проекта: {project_path}/{project_name}")
        
        try:
            project_dir = Path(project_path) / project_name
            if not self._create_directory(project_dir):
                return False
            
            # Создаем базовые файлы
            basic_structure = {
                'modules': [],
                'files': {
                    '__init__.py': '# Package initialization\n',
                    'main.py': '#!/usr/bin/env python3\n"""Main module"""\n\ndef main():\n    print("Hello from AI Code Assistant!")\n\n\nif __name__ == "__main__":\n    main()\n',
                    'README.md': f'# {project_name}\n\nProject created by AI Code Assistant\n',
                    'requirements.txt': '# Project dependencies\n'
                }
            }
            
            return self.create_project_from_ai_schema(basic_structure, str(project_dir))
            
        except Exception as e:
            logger.error(f"Ошибка при создании базового проекта: {e}")
            return False
    
    def _create_directory(self, directory: Path) -> bool:
        """Создает директорию если она не существует"""
        try:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Создана директория: {directory}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании директории {directory}: {e}")
            return False
    
    def _create_directories_structure(self, base_dir: Path, modules: List[str]):
        """Создает структуру директорий"""
        created_dirs = set()
        
        for module_path in modules:
            clean_path = module_path.strip('/')
            if not clean_path:
                continue
                
            parts = clean_path.split('/')
            current_path = base_dir
            
            for part in parts:
                current_path = current_path / part
                if self._create_directory(current_path):
                    created_dirs.add(str(current_path))
        
        logger.debug(f"Создано директорий: {len(created_dirs)}")
    
    def _create_files(self, base_dir: Path, files: Dict[str, str]):
        """Создает файлы проекта"""
        files_created = 0
        
        for file_path, content in files.items():
            file_full_path = base_dir / file_path
            
            parent_dir = file_full_path.parent
            if not parent_dir.exists():
                self._create_directory(parent_dir)
            
            try:
                file_full_path.write_text(content, encoding='utf-8')
                files_created += 1
                logger.debug(f"Создан файл: {file_full_path}")
            except Exception as e:
                logger.warning(f"Не удалось создать файл {file_full_path}: {e}")
        
        logger.info(f"Файлов создано: {files_created}/{len(files)}")