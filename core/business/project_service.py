# core/business/project_service.py

from abc import ABC, abstractmethod

class IProjectService(ABC):
    def create_project(self, path, name): pass
    def open_project(self, path): pass
    def save_project(self): pass
    def close_project(self): pass
    def create_structure_from_ai(self, schema): pass

class ProjectService(IProjectService):
    """
    Сервис управления проектом: бизнес-логика, коммуникация с репозиторием.
    """
    def __init__(self, repository, schema_parser=None):
        self.repository = repository      # IProjectRepository
        self.schema_parser = schema_parser  # AISchemaParser (опционально)
        self.project_path = None
        self.project_name = None
        self.opened = False

    def create_project(self, path, name):
        """
        Создать базовый проект.
        """
        result = self.repository.create_basic_python_project(path, name)
        if result:
            self.project_path = path
            self.project_name = name
            self.opened = True
        return result

    def open_project(self, path):
        """
        Открыть существующий проект.
        """
        result = self.repository.open(path)
        if result:
            self.project_path = path
            self.project_name = self._extract_project_name(path)
            self.opened = True
        return result

    def save_project(self):
        """
        Сохранить все изменения проекта.
        """
        if not self.opened or not self.project_path:
            return False
        return self.repository.save(self.project_path)

    def close_project(self):
        """
        Закрыть проект, очистить состояние.
        """
        self.project_path = None
        self.project_name = None
        self.opened = False
        return True

    def create_structure_from_ai(self, schema):
        """
        Сгенерировать структуру по AI-схеме: парсинг и запись.
        """
        if not self.opened or not self.project_path or self.schema_parser is None:
            return False
        structure = self.schema_parser.parse(schema)
        if not structure:
            return False
        return self.repository.create_structure(self.project_path, structure)

    def _extract_project_name(self, path):
        import os
        return os.path.basename(str(path).rstrip("/\\"))