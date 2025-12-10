# core/business/project_service.py

from abc import ABC, abstractmethod
from core.business.project_creator_service import ProjectCreatorService
from core.business.ai_schema_service import AISchemaService  # ← ИСПРАВЛЕНО!
from core.business.error_handler import handle_errors
from core.business.project_structure_service import ProjectStructureService
from core.data.project_repository import ProjectRepository  # ← ДОБАВЛЕНО!

import logging
logger = logging.getLogger('ai_code_assistant')


class IProjectService(ABC):
    @abstractmethod
    def create_project(self, path, name): pass
    
    @abstractmethod
    def open_project(self, path): pass
    
    @abstractmethod
    def save_project(self): pass
    
    @abstractmethod
    def close_project(self): pass
    
    @abstractmethod
    def create_structure_from_ai(self, schema): pass


class ProjectService(IProjectService):
    """Сервис управления проектом с реальной реализацией."""
    
    def __init__(self, repository=None):  # ← ДОБАВЛЕН ПАРАМЕТР ПО УМОЛЧАНИЮ
        self.repository = repository or ProjectRepository()  # ← СОЗДАЕМ ПО УМОЛЧАНИЮ
        self.project_creator = ProjectCreatorService()
        self.schema_parser = AISchemaService()  # ← ИСПРАВЛЕНО!
        self.project_structure_service = ProjectStructureService(self.repository)
        self.project_path = None
        self.project_name = None
        self.opened = False
        logger.debug("ProjectService инициализирован")
    
    @handle_errors(default_return=False)
    def create_project(self, path, name):
        """Создать базовый проект."""
        logger.info(f"Создание проекта: {path}/{name}")
        
        result = self.project_creator.create_basic_python_project(path, name)
        if result:
            self.project_path = f"{path}/{name}"
            self.project_name = name
            self.opened = True
            logger.info(f"Проект создан: {self.project_path}")
            
            # Открываем созданный проект
            return self.open_project(self.project_path)
        else:
            logger.error(f"Не удалось создать проект: {path}/{name}")
            return False
    
    @handle_errors(default_return=False)
    def open_project(self, path):
        """Открыть существующий проект."""
        logger.info(f"Открытие проекта: {path}")
        
        result = self.repository.open(path)
        if result:
            self.project_path = path
            self.project_name = self._extract_project_name(path)
            self.opened = True
            logger.info(f"Проект открыт: {path}")
        else:
            logger.error(f"Не удалось открыть проект: {path}")
        
        return result
    
    @handle_errors(default_return=False)
    def save_project(self):
        """Сохранить все изменения проекта."""
        if not self.opened or not self.project_path:
            logger.warning("Нет открытого проекта для сохранения")
            return False
        
        logger.info(f"Сохранение проекта: {self.project_path}")
        
        # Вызываем сохранение через репозиторий
        result = self.repository.save(self.project_path)
        
        if result:
            logger.info(f"Проект сохранен: {self.project_path}")
        else:
            logger.error(f"Не удалось сохранить проект: {self.project_path}")
        
        return result
    
    @handle_errors(default_return=False)
    def close_project(self):
        """Закрыть проект, очистить состояние."""
        logger.info(f"Закрытие проекта: {self.project_path}")
        
        # Закрываем через репозиторий
        result = self.repository.close()
        
        if result:
            self.project_path = None
            self.project_name = None
            self.opened = False
            logger.info("Проект закрыт успешно")
        else:
            logger.error("Не удалось закрыть проект")
        
        return result
    
    @handle_errors(default_return=False)
    def create_structure_from_ai(self, schema):
        """Сгенерировать структуру по AI-схеме."""
        if not self.opened or not self.project_path:
            logger.warning("Нет открытого проекта для создания структуры")
            return False
        
        logger.info(f"Создание структуры из AI схемы")
        
        if isinstance(schema, str):
            # Если schema - это текст, парсим его
            structure = self.schema_parser.parse(schema)
        else:
            # Если schema уже словарь
            structure = schema
        
        if not structure:
            logger.error("Не удалось распарсить AI схему")
            return False
        
        # Создаем структуру в проекте
        return self.project_creator.create_project_from_ai_schema(structure, self.project_path)
    
    def _extract_project_name(self, path):
        import os
        return os.path.basename(str(path).rstrip("/\\"))
    
    # Новые методы для работы со структурой проекта
    
    @handle_errors(default_return={})
    def get_project_structure(self):
        """Получить полную структуру проекта с AST анализом."""
        if not self.opened or not self.project_path:
            logger.warning("Нет открытого проекта для получения структуры")
            return {}
        
        return self.project_structure_service.get_full_project_structure(self.project_path)
    
    @handle_errors(default_return={})
    def get_file_structure(self):
        """Получить только файловую структуру проекта (быстрее)."""
        if not self.opened or not self.project_path:
            logger.warning("Нет открытого проекта для получения структуры")
            return {}
        
        return self.project_structure_service.get_file_structure(self.project_path)
    
    @handle_errors(default_return={})
    def get_ast_structure(self):
        """Получить только AST структуру проекта."""
        if not self.opened or not self.project_path:
            logger.warning("Нет открытого проекта для получения AST структуры")
            return {}
        
        return self.project_structure_service.get_ast_structure(self.project_path)
    
    @handle_errors(default_return={})
    def get_file_with_ast(self, file_path: str):
        """Получить информацию о файле с его AST структурой."""
        if not self.opened or not self.project_path:
            logger.warning("Нет открытого проекта для получения файла")
            return {}
        
        return self.project_structure_service.get_file_with_ast(file_path, self.project_path)
    
    @handle_errors(default_return={})
    def get_project_statistics(self):
        """Получить статистику по проекту."""
        structure = self.get_project_structure()
        return structure.get('statistics', {}) if structure else {}
    
    # Свойства для доступа к состоянию
    @property
    def is_opened(self):
        """Проверяет, открыт ли проект."""
        return self.opened
    
    @property
    def current_project_info(self):
        """Возвращает информацию о текущем проекте."""
        return {
            'path': self.project_path,
            'name': self.project_name,
            'opened': self.opened
        }