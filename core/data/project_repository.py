# core/data/project_repository.py

from abc import ABC, abstractmethod
from pathlib import Path

class IProjectRepository(ABC):
    def create_basic_python_project(self, path, name): pass
    def open(self, path): pass
    def save(self, path): pass
    def close(self): pass
    def create_structure(self, path, structure): pass
    def write_current_file(self, content: str) -> bool: pass
    def add_ai_code_to_current(self, ai_code: str) -> bool: pass
    def replace_code_in_file(self, file_path: str, node_name: str, new_code: str) -> bool: pass
    def get_project_structure(self): pass
    def read_file(self, file_path: str) -> str: pass

class ProjectRepository(IProjectRepository):
    """
    Репозиторий для работы с проектом, файлами и структурой.
    """
    def __init__(self):
        self.current_file_path = None
        self.project_path = None

    def create_basic_python_project(self, path, name):
        try:
            self.project_path = Path(path) / name
            self.project_path.mkdir(parents=True, exist_ok=True)
            (self.project_path / "__init__.py").touch()
            (self.project_path / "main.py").write_text("# main file\n", encoding="utf-8")
            return True
        except Exception as e:
            print(f"Ошибка создания проекта: {e}")
            return False

    def open(self, path):
        p = Path(path)
        if p.exists() and p.is_dir():
            self.project_path = p
            return True
        return False

    def save(self, path):
        # Для примера — всегда true, в реальности можно сериализовать состояние проекта
        return True

    def close(self):
        self.project_path = None
        self.current_file_path = None
        return True

    def create_structure(self, path, structure):
        try:
            base_dir = Path(path)
            for module in structure.get('modules', []):
                module_dir = base_dir / module.strip("/")
                module_dir.mkdir(parents=True, exist_ok=True)
                (module_dir / "__init__.py").touch()
            for file_path, content in structure.get('files', {}).items():
                file_full_path = base_dir / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"Ошибка создания структуры: {e}")
            return False

    def write_current_file(self, content: str) -> bool:
        try:
            if not self.current_file_path:
                return False
            Path(self.current_file_path).write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"Ошибка записи файла: {e}")
            return False

    def add_ai_code_to_current(self, ai_code: str) -> bool:
        try:
            if not self.current_file_path:
                return False
            current_content = Path(self.current_file_path).read_text(encoding="utf-8")
            appended_content = f"{current_content}\n# == AI CODE ==\n{ai_code}"
            Path(self.current_file_path).write_text(appended_content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"Ошибка добавления AI-кода: {e}")
            return False

    def replace_code_in_file(self, file_path: str, node_name: str, new_code: str) -> bool:
        try:
            p = Path(file_path)
            lines = p.read_text(encoding="utf-8").splitlines()
            out_lines = []
            replaced = False
            for line in lines:
                if node_name in line and not replaced:
                    out_lines.append(new_code)
                    replaced = True
                else:
                    out_lines.append(line)
            p.write_text("\n".join(out_lines), encoding="utf-8")
            return replaced
        except Exception as e:
            print(f"Ошибка замены кода: {e}")
            return False

    def get_project_structure(self):
        """
        Сканирует директорию проекта, возвращает dict: {'modules': [...], 'files': {...}}
        """
        structure = {'modules': [], 'files': {}}
        if not self.project_path:
            return structure
        for path in self.project_path.glob("**/"):
            if path.is_dir():
                rel = str(path.relative_to(self.project_path))
                if rel and rel != '.':
                    structure['modules'].append(rel)
        for path in self.project_path.glob("**/*.py"):
            rel = str(path.relative_to(self.project_path))
            structure['files'][rel] = path.read_text(encoding='utf-8')
        return structure

    def read_file(self, file_path: str) -> str:
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            return ""