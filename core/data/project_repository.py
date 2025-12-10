# core/data/project_repository.py

from abc import ABC, abstractmethod
from pathlib import Path
import os
from typing import Dict, Any
from .file_provider import FileProvider
import logging

logger = logging.getLogger('ai_code_assistant')


class IProjectRepository(ABC):
    @abstractmethod
    def create_basic_python_project(self, path, name): pass
    
    @abstractmethod
    def open(self, path): pass
    
    @abstractmethod
    def save(self, path): pass
    
    @abstractmethod
    def close(self): pass
    
    @abstractmethod
    def create_structure(self, path, structure): pass
    
    @abstractmethod
    def write_current_file(self, content: str) -> bool: pass
    
    @abstractmethod
    def add_ai_code_to_current(self, ai_code: str) -> bool: pass
    
    @abstractmethod
    def replace_code_in_file(self, file_path: str, node_name: str, new_code: str) -> bool: pass
    
    @abstractmethod
    def get_project_structure(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    def read_file(self, file_path: str) -> str: pass
    
    @abstractmethod
    def write_file(self, file_path: str, content: str) -> bool: pass


class ProjectRepository(IProjectRepository):
    """Репозиторий для работы с проектом, файлами и структурой."""
    
    def __init__(self):
        self.current_file_path = None
        self.project_path = None
        self.file_provider = FileProvider
        logger.debug("Инициализирован ProjectRepository")
    
    def create_basic_python_project(self, path, name):
        """Создает базовый Python проект."""
        try:
            self.project_path = Path(path) / name
            
            if not self.file_provider.create_directory(str(self.project_path)):
                return False
            
            # Создаем базовые файлы
            files_to_create = {
                "__init__.py": "# Package initialization\n",
                "main.py": '#!/usr/bin/env python3\n"""Main module"""\n\ndef main():\n    print("Hello from AI Code Assistant!")\n\n\nif __name__ == "__main__":\n    main()\n',
                "README.md": f"# {name}\n\nПроект создан с помощью AI Code Assistant\n",
                "requirements.txt": "# Зависимости проекта\n"
            }
            
            for filename, content in files_to_create.items():
                file_path = self.project_path / filename
                if not self.file_provider.write_file(str(file_path), content):
                    return False
            
            logger.info(f"Базовый проект создан: {self.project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания проекта: {e}")
            return False
    
    def open(self, path):
        """Открывает проект."""
        p = Path(path)
        if p.exists() and p.is_dir():
            self.project_path = p
            logger.info(f"Проект открыт: {path}")
            return True
        logger.warning(f"Проект не существует или не является директорией: {path}")
        return False
    
    def save(self, path):
        """Сохраняет состояние проекта."""
        try:
            if self.project_path and self.project_path.exists():
                logger.info(f"Проект сохранен: {self.project_path}")
                return True
            else:
                logger.error(f"Ошибка сохранения: проект не открыт или не существует")
                return False
        except Exception as e:
            logger.error(f"Ошибка сохранения проекта: {e}")
            return False
    
    def close(self):
        """Закрывает проект."""
        self.project_path = None
        self.current_file_path = None
        logger.info("Проект закрыт")
        return True
    
    def create_structure(self, path, structure):
        """Создает структуру проекта."""
        try:
            base_dir = Path(path)
            
            # Создаем директории модулей
            for module in structure.get('modules', []):
                module_dir = base_dir / module.strip("/")
                self.file_provider.create_directory(str(module_dir))
                
                # Создаем __init__.py в каждой папке Python модуля
                init_file = module_dir / "__init__.py"
                self.file_provider.write_file(str(init_file), "# Package initialization\n")
            
            # Создаем файлы
            for file_path, content in structure.get('files', {}).items():
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: создаем абсолютный путь
                if not Path(file_path).is_absolute():
                    file_full_path = base_dir / file_path
                else:
                    file_full_path = Path(file_path)
                    
                self.file_provider.create_directory(str(file_full_path.parent))
                self.file_provider.write_file(str(file_full_path), content)
            
            logger.info(f"Структура создана в: {path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания структуры: {e}")
            return False
    
    def write_current_file(self, content: str) -> bool:
        """Записывает содержимое в текущий файл."""
        try:
            if not self.current_file_path:
                logger.error("Нет текущего файла для записи")
                return False
            
            success = self.file_provider.write_file(self.current_file_path, content)
            if success:
                logger.info(f"Файл сохранен: {self.current_file_path}")
            return success
        except Exception as e:
            logger.error(f"Ошибка записи файла: {e}")
            return False
    
    def add_ai_code_to_current(self, ai_code: str) -> bool:
        """Добавляет AI-код в текущий файл."""
        try:
            if not self.current_file_path:
                logger.error("Нет текущего файла для добавления AI-кода")
                return False
            
            current_content = self.file_provider.read_file(self.current_file_path)
            if current_content is None:
                current_content = ""
            
            appended_content = f"{current_content}\n\n# == AI CODE ==\n{ai_code}\n"
            
            success = self.file_provider.write_file(self.current_file_path, appended_content)
            if success:
                logger.info(f"AI-код добавлен в файл: {self.current_file_path}")
            return success
        except Exception as e:
            logger.error(f"Ошибка добавления AI-кода: {e}")
            return False
    
    def replace_code_in_file(self, file_path: str, node_name: str, new_code: str) -> bool:
        """Заменяет код в файле."""
        try:
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: получаем абсолютный путь
            if not Path(file_path).is_absolute() and self.project_path:
                file_path = str(self.project_path / file_path)
            
            content = self.file_provider.read_file(file_path)
            if content is None:
                content = ""
            
            lines = content.splitlines()
            out_lines = []
            replaced = False
            
            for line in lines:
                if node_name in line and not replaced:
                    out_lines.append(new_code)
                    replaced = True
                else:
                    out_lines.append(line)
            
            if replaced:
                new_content = "\n".join(out_lines)
                logger.info(f"Код заменен в файле: {file_path}, элемент: {node_name}")
            else:
                new_content = content + "\n" + new_code
                logger.info(f"Элемент не найден, код добавлен в конец файла: {file_path}")
            
            return self.file_provider.write_file(file_path, new_content)
        except Exception as e:
            logger.error(f"Ошибка замены кода: {e}")
            return False
    
    def get_project_structure(self) -> Dict[str, Any]:
        """Сканирует директорию проекта и возвращает файловую структуру."""
        structure = {
            'modules': [],
            'files': {},
            'directories': [],
            'project_path': str(self.project_path) if self.project_path else None
        }
        
        if not self.project_path or not self.project_path.exists():
            logger.warning("Попытка получить структуру без открытого проекта")
            return structure
        
        try:
            # Сканируем директорию проекта
            for item in self.project_path.rglob("*"):
                if item.is_file() and item.suffix == '.py':
                    # Пропускаем файлы в __pycache__
                    if '__pycache__' in str(item):
                        continue
                    
                    rel_path = str(item.relative_to(self.project_path))
                    
                    # Определяем модуль
                    module_path = str(item.parent.relative_to(self.project_path))
                    if module_path == '.':
                        module_name = ''
                    else:
                        module_name = module_path.replace(os.sep, '.')
                    
                    # Добавляем модуль если еще нет
                    if module_name and module_name not in structure['modules']:
                        structure['modules'].append(module_name)
                    
                    # Добавляем директорию
                    if module_path not in structure['directories'] and module_path != '.':
                        structure['directories'].append(module_path)
                    
                    # Читаем содержимое файла
                    try:
                        content = self.file_provider.read_file(str(item))  # Абсолютный путь
                        if content is not None:
                            structure['files'][rel_path] = {
                                'path': str(item),  # Абсолютный путь
                                'module': module_name,
                                'name': item.name,
                                'content': content
                            }
                    except Exception as e:
                        logger.error(f"Ошибка чтения файла {item}: {e}")
                        structure['files'][rel_path] = {
                            'path': str(item),
                            'module': module_name,
                            'name': item.name,
                            'content': f"# Ошибка чтения: {e}"
                        }
                
                elif item.is_dir() and item != self.project_path:
                    # Добавляем директории (кроме служебных)
                    rel_path = str(item.relative_to(self.project_path))
                    if ('__pycache__' not in rel_path and 
                        not rel_path.startswith('.') and
                        rel_path not in structure['directories']):
                        structure['directories'].append(rel_path)
            
            logger.info(f"Файловая структура получена: {len(structure['files'])} файлов, "
                       f"{len(structure['directories'])} директорий")
            return structure
            
        except Exception as e:
            logger.error(f"Ошибка получения файловой структуры: {e}")
            return structure
    
    def read_file(self, file_path: str) -> str:
        """Читает содержимое файла."""
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: если путь относительный, делаем его абсолютным относительно проекта
        path = Path(file_path)
        if not path.is_absolute() and self.project_path:
            file_path = str(self.project_path / file_path)
        
        content = self.file_provider.read_file(file_path)
        if content is None:
            return ""
        return content
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Записывает содержимое в файл."""
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: если путь относительный, делаем его абсолютным относительно проекта
        path = Path(file_path)
        if not path.is_absolute() and self.project_path:
            file_path = str(self.project_path / file_path)
        
        return self.file_provider.write_file(file_path, content)
    
    # Дополнительные методы для удобства
    
    def set_current_file(self, file_path: str):
        """Устанавливает текущий файл."""
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: если путь относительный, делаем его абсолютным
        path = Path(file_path)
        if not path.is_absolute() and self.project_path:
            file_path = str(self.project_path / file_path)
        
        self.current_file_path = file_path
        logger.debug(f"Текущий файл установлен: {file_path}")
    
    def get_current_file(self) -> str:
        """Возвращает текущий файл."""
        return self.current_file_path
    
    def get_project_path(self) -> str:
        """Возвращает путь к проекту."""
        return str(self.project_path) if self.project_path else None
    
    def project_exists(self) -> bool:
        """Проверяет, существует ли проект."""
        return self.project_path is not None and self.project_path.exists()
    
    def scan_project_files(self) -> Dict[str, Any]:
        """Расширенное сканирование файлов проекта."""
        if not self.project_exists():
            return {}
        
        files_info = {}
        for item in self.project_path.rglob("*"):
            if item.is_file():
                rel_path = str(item.relative_to(self.project_path))
                files_info[rel_path] = {
                    'size': self.file_provider.get_file_size(str(item)),
                    'extension': item.suffix,
                    'path': str(item)  # Абсолютный путь
                }
        
        return files_info
    
    def get_absolute_path(self, relative_path: str) -> str:
        """Возвращает абсолютный путь для относительного пути."""
        if not self.project_path:
            return relative_path
        
        return str(self.project_path / relative_path)