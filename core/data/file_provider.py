# core/data/file_provider.py

from pathlib import Path

class FileProvider:
    """
    Провайдер низкоуровневых операций с файлами и директориями.
    Используется сервисами и репозиториями для прямой работы с ФС.
    """
    @staticmethod
    def read_file(file_path: str) -> str:
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            return ""

    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            Path(file_path).write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"Ошибка записи файла: {e}")
            return False

    @staticmethod
    def list_dir(dir_path: str):
        try:
            return [str(p) for p in Path(dir_path).iterdir()]
        except Exception as e:
            print(f"Ошибка чтения директории: {e}")
            return []

    @staticmethod
    def file_exists(file_path: str) -> bool:
        return Path(file_path).exists()

    @staticmethod
    def dir_exists(dir_path: str) -> bool:
        path = Path(dir_path)
        return path.exists() and path.is_dir()

    @staticmethod
    def remove_file(file_path: str) -> bool:
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
            return False

    @staticmethod
    def remove_dir(dir_path: str) -> bool:
        try:
            path = Path(dir_path)
            for child in path.iterdir():
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    FileProvider.remove_dir(str(child))
            path.rmdir()
            return True
        except Exception as e:
            print(f"Ошибка удаления директории: {e}")
            return False

    @staticmethod
    def find_files_by_pattern(dir_path: str, pattern: str):
        """
        Поиск файлов по маске, например '*.py'
        """
        try:
            return [str(p) for p in Path(dir_path).glob(pattern)]
        except Exception as e:
            print(f"Ошибка поиска файлов: {e}")
            return []