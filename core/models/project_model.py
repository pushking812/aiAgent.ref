# core/models/project_model.py

class ProjectModel:
    """
    Модель данных для структуры проекта.
    """
    def __init__(self, name: str, modules=None, files=None):
        self.name = name                    # Название проекта
        self.modules = modules or []        # Список модулей (папки, относительные пути)
        self.files = files or {}            # Словарь файлов: {путь: содержимое}

    def add_module(self, module_path: str):
        """
        Добавить модуль/папку в структуру.
        """
        if module_path and module_path not in self.modules:
            self.modules.append(module_path)

    def add_file(self, file_path: str, content: str = ""):
        """
        Добавить файл с содержимым.
        """
        self.files[file_path] = content

    def get_file_content(self, file_path: str) -> str:
        """
        Получить содержимое файла по пути.
        """
        return self.files.get(file_path, "")

    def remove_file(self, file_path: str):
        """
        Удалить файл из структуры.
        """
        if file_path in self.files:
            del self.files[file_path]

    def remove_module(self, module_path: str):
        """
        Удалить модуль (и все файлы внутри, если нужно).
        """
        if module_path in self.modules:
            self.modules.remove(module_path)
        files_to_remove = [fp for fp in self.files if fp.startswith(module_path)]
        for fp in files_to_remove:
            del self.files[fp]

    def list_files(self):
        return list(self.files.keys())

    def list_modules(self):
        return list(self.modules)

    def __repr__(self):
        return f"ProjectModel(name={self.name}, modules={self.modules}, files={list(self.files.keys())})"