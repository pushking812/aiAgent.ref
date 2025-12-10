# core/data/file_provider.py

from pathlib import Path
import os
from typing import List
import logging

logger = logging.getLogger('ai_code_assistant')


class FileProvider:
    """
    Унифицированный провайдер низкоуровневых операций с файлами и директориями.
    Используется сервисами и репозиториями для прямой работы с ФС.
    """
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Читает содержимое файла"""
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Ошибка чтения файла {file_path}: {e}")
            return ""

    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """Записывает содержимое в файл"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            logger.debug(f"Файл записан: {file_path} ({len(content)} символов)")
            return True
        except Exception as e:
            logger.error(f"Ошибка записи файла {file_path}: {e}")
            return False

    @staticmethod
    def list_dir(dir_path: str) -> List[str]:
        """Список содержимого директории"""
        try:
            return [str(p) for p in Path(dir_path).iterdir()]
        except Exception as e:
            logger.error(f"Ошибка чтения директории {dir_path}: {e}")
            return []

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Проверяет существование файла"""
        return Path(file_path).exists()

    @staticmethod
    def dir_exists(dir_path: str) -> bool:
        """Проверяет существование директории"""
        path = Path(dir_path)
        return path.exists() and path.is_dir()

    @staticmethod
    def remove_file(file_path: str) -> bool:
        """Удаляет файл"""
        try:
            Path(file_path).unlink(missing_ok=True)
            logger.debug(f"Файл удален: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления файла {file_path}: {e}")
            return False

    @staticmethod
    def remove_dir(dir_path: str) -> bool:
        """Рекурсивно удаляет директорию"""
        try:
            path = Path(dir_path)
            for child in path.iterdir():
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    FileProvider.remove_dir(str(child))
            path.rmdir()
            logger.debug(f"Директория удалена: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления директории {dir_path}: {e}")
            return False

    @staticmethod
    def find_files_by_pattern(dir_path: str, pattern: str) -> List[str]:
        """
        Поиск файлов по маске, например '*.py'
        """
        try:
            return [str(p) for p in Path(dir_path).glob(pattern)]
        except Exception as e:
            logger.error(f"Ошибка поиска файлов в {dir_path} с шаблоном {pattern}: {e}")
            return []
    
    @staticmethod
    def create_directory(directory: str) -> bool:
        """Создает директорию если она не существует"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Директория создана/существует: {directory}")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания директории {directory}: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Возвращает размер файла в байтах"""
        try:
            return Path(file_path).stat().st_size
        except Exception as e:
            logger.error(f"Ошибка получения размера файла {file_path}: {e}")
            return 0
    
    @staticmethod
    def get_relative_path(base_path: str, full_path: str) -> str:
        """Возвращает относительный путь"""
        try:
            return str(Path(full_path).relative_to(base_path))
        except Exception as e:
            logger.error(f"Ошибка получения относительного пути: {e}")
            return full_path
    
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """Копирует файл"""
        try:
            import shutil
            shutil.copy2(source, destination)
            logger.debug(f"Файл скопирован: {source} -> {destination}")
            return True
        except Exception as e:
            logger.error(f"Ошибка копирования файла {source} -> {destination}: {e}")
            return False