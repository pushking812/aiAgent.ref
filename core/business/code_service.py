# core/business/code_service.py

from abc import ABC, abstractmethod
from core.business.code_manager import CodeManager
from core.business.diff_engine import DiffEngine
from core.business.ast_service import ASTService
from core.business.change_service import ChangeManager
from core.business.error_handler import handle_errors

import logging
logger = logging.getLogger('ai_code_assistant')


class ICodeService(ABC):
    @abstractmethod
    def save_current_file(self, content: str) -> bool: pass
    
    @abstractmethod
    def add_ai_code(self, ai_code: str) -> bool: pass
    
    @abstractmethod
    def replace_code(self, file_path: str, node_name: str, new_code: str) -> bool: pass
    
    @abstractmethod
    def get_file_content(self, file_path: str) -> str: pass
    
    @abstractmethod
    def analyze_ai_code(self, ai_code: str, project_tree, target_file_path: str = ""): pass
    
    @abstractmethod
    def get_diff(self, old_code: str, new_code: str) -> str: pass
    
    @abstractmethod
    def get_change_manager(self): pass
    
    @abstractmethod
    def add_code(self, file_path: str, code: str, position: str = 'end') -> bool: pass
    
    @abstractmethod
    def delete_code(self, file_path: str, entity_name: str) -> bool: pass


class CodeService(ICodeService):
    """Сервис для управления исходным и AI-кодом с реальной реализацией."""
    
    def __init__(self, repository, ast_service=None):
        self.repository = repository
        self.code_manager = CodeManager()
        self.diff_engine = DiffEngine()
        self.ast_service = ast_service or ASTService()
        self._change_manager = ChangeManager()
    
    @handle_errors(default_return=False)
    def save_current_file(self, content: str) -> bool:
        """Сохраняет текущий открытый файл."""
        logger.debug("Сохранение текущего файла")
        return self.repository.write_current_file(content)
    
    @handle_errors(default_return=False)
    def add_ai_code(self, ai_code: str) -> bool:
        """Добавляет AI-код в текущий файл."""
        logger.info(f"Добавление AI-кода: {len(ai_code)} символов")
        
        # Получаем текущий файл
        current_file = self.repository.current_file_path
        if not current_file:
            logger.error("Нет открытого файла для добавления AI-кода")
            return False
        
        # Получаем текущее содержимое
        current_content = self.get_file_content(current_file)
        
        # Добавляем AI-код
        new_content = current_content.rstrip() + '\n\n' + ai_code + '\n'
        
        # Сохраняем
        return self.repository.write_file(current_file, new_content)
    
    @handle_errors(default_return=False)
    def replace_code(self, file_path: str, node_name: str, new_code: str) -> bool:
        """Заменяет кусок кода в файле."""
        logger.info(f"Замена кода: {file_path}, {node_name}")
        
        # Получаем текущий код
        old_content = self.get_file_content(file_path)
        
        # Простая замена по имени узла
        # (В реальной реализации здесь будет использоваться AST парсинг)
        lines = old_content.split('\n')
        new_lines = []
        replaced = False
        
        for line in lines:
            if node_name in line and not replaced:
                new_lines.append(new_code)
                replaced = True
            else:
                new_lines.append(line)
        
        if replaced:
            new_content = '\n'.join(new_lines)
            return self.repository.write_file(file_path, new_content)
        else:
            logger.warning(f"Элемент '{node_name}' не найден в файле {file_path}")
            return False
    
    @handle_errors(default_return="")
    def get_file_content(self, file_path: str) -> str:
        """Получить содержимое файла - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ."""
        logger.debug(f"Получение содержимого файла: {file_path}")
        return self.repository.read_file(file_path)
    
    @handle_errors(default_return=[])
    def analyze_ai_code(self, ai_code: str, project_tree, target_file_path: str = ""):
        """Анализирует AI-код и возвращает изменения - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ."""
        logger.info(f"Анализ AI-кода: {len(ai_code)} символов")
        
        try:
            # Используем CodeManager для анализа
            return self.code_manager.analyze_ai_code(ai_code, project_tree, target_file_path)
        except Exception as e:
            logger.error(f"Ошибка при анализе AI-кода: {e}")
            return []
    
    @handle_errors(default_return="")
    def get_diff(self, old_code: str, new_code: str) -> str:
        """Получить различия между двумя версиями кода - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ."""
        logger.debug("Генерация diff")
        diff = self.diff_engine.generate_diff(old_code, new_code)
        return self.diff_engine.format_diff_for_display(diff)
    
    def get_change_manager(self):
        """Возвращает менеджер изменений - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ."""
        return self._change_manager
    
    @handle_errors(default_return=False)
    def add_code(self, file_path: str, code: str, position: str = 'end') -> bool:
        """Добавляет код в файл."""
        logger.info(f"Добавление кода в файл: {file_path}")
        
        content = self.get_file_content(file_path)
        
        if position == 'end':
            new_content = content.rstrip() + '\n\n' + code + '\n'
        elif position == 'beginning':
            new_content = code + '\n\n' + content
        else:
            # Простая вставка в середину (упрощенная реализация)
            lines = content.split('\n')
            try:
                pos = int(position)
                if 0 <= pos < len(lines):
                    lines.insert(pos, code)
                    new_content = '\n'.join(lines)
                else:
                    new_content = content + '\n\n' + code + '\n'
            except ValueError:
                new_content = content + '\n\n' + code + '\n'
        
        return self.repository.write_file(file_path, new_content)
    
    @handle_errors(default_return=False)
    def delete_code(self, file_path: str, entity_name: str) -> bool:
        """Удаляет код из файла."""
        logger.info(f"Удаление кода из файла: {file_path}, элемент: {entity_name}")
        
        content = self.get_file_content(file_path)
        lines = content.split('\n')
        new_lines = []
        
        # Простая реализация - удаляем строки, содержащие имя элемента
        # (В реальной реализации будет использоваться AST парсинг)
        for line in lines:
            if entity_name not in line:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        # Если ничего не удалили, возвращаем False
        if len(new_lines) == len(lines):
            logger.warning(f"Элемент '{entity_name}' не найден в файле {file_path}")
            return False
        
        return self.repository.write_file(file_path, new_content)
    
    def set_ast_service(self, ast_service: ASTService):
        """Устанавливает AST сервис."""
        self.ast_service = ast_service
        logger.debug("AST сервис установлен")
    
    def get_ast_service(self) -> ASTService:
        """Возвращает AST сервис."""
        return self.ast_service