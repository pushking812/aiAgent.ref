# core/business/code_service.py

from abc import ABC, abstractmethod

class ICodeService(ABC):
    def save_current_file(self, content: str) -> bool: pass
    def add_ai_code(self, ai_code: str) -> bool: pass
    def replace_code(self, file_path: str, node_name: str, new_code: str) -> bool: pass
    def get_file_content(self, file_path: str) -> str: pass

class CodeService(ICodeService):
    """
    Сервис для управления исходным и AI-кодом;
    содержит бизнес-логику для операций с кодом.
    """
    def __init__(self, repository):
        self.repository = repository  # IProjectRepository

    def save_current_file(self, content: str) -> bool:
        """
        Сохраняет текущий открытый файл.
        """
        return self.repository.write_current_file(content)

    def add_ai_code(self, ai_code: str) -> bool:
        """
        Добавляет AI-код в текущий файл (например, в конце или по специальной метке).
        """
        return self.repository.add_ai_code_to_current(ai_code)

    def replace_code(self, file_path: str, node_name: str, new_code: str) -> bool:
        """
        Заменяет кусок кода в файле (например, функцию/метод на AI-код).
        """
        return self.repository.replace_code_in_file(file_path, node_name, new_code)

    def get_file_content(self, file_path: str) -> str:
        """
        Получить содержимое файла (для отображения или сравнения).
        """
        from core.data.file_provider import FileProvider
        return FileProvider.read_file(file_path)