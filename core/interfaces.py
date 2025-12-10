# core/interfaces.py

"""
Базовые интерфейсы для унификации архитектуры приложения.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path


class IProjectCreator(ABC):
    """Интерфейс создания проектов"""
    
    @abstractmethod
    def create_project_from_ai_schema(self, schema: Dict[str, Any], project_path: str) -> bool:
        """Создает проект на основе схемы от AI"""
        pass
    
    @abstractmethod
    def create_basic_python_project(self, project_path: str, project_name: str) -> bool:
        """Создает базовую структуру Python проекта"""
        pass


class ICodeAnalyzer(ABC):
    """Интерфейс анализа кода"""
    
    @abstractmethod
    def analyze_project(self, project_path: str) -> List[Dict[str, Any]]:
        """Анализирует весь проект"""
        pass
    
    @abstractmethod
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Анализирует один файл"""
        pass


class IASTService(ABC):
    """Интерфейс работы с AST"""
    
    @abstractmethod
    def parse_project(self, directory_path: str) -> Dict[str, Any]:
        """Парсит весь проект"""
        pass
    
    @abstractmethod
    def parse_module(self, file_path: str) -> Optional[Any]:
        """Парсит один модуль"""
        pass


class ISchemaParser(ABC):
    """Интерфейс парсера схем"""
    
    @abstractmethod
    def parse(self, schema_text: str) -> Dict[str, Any]:
        """Парсит схему"""
        pass


class IChangeManager(ABC):
    """Интерфейс управления изменениями"""
    
    @abstractmethod
    def add_change(self, change: Any) -> None:
        """Добавляет изменение"""
        pass
    
    @abstractmethod
    def apply_all_changes(self) -> bool:
        """Применяет все изменения"""
        pass


class IDiffEngine(ABC):
    """Интерфейс движка сравнения"""
    
    @abstractmethod
    def generate_diff(self, old_code: str, new_code: str) -> List[Any]:
        """Генерирует различия"""
        pass
    
    @abstractmethod
    def format_diff_for_display(self, diff: List[Any]) -> str:
        """Форматирует diff для отображения"""
        pass