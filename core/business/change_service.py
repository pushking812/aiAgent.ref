# core/business/change_service.py

import time
from typing import List, Tuple, Optional
from core.models.code_model import CodeNode
from .error_handler import handle_errors

import logging
logger = logging.getLogger('ai_code_assistant')


class CodeChange:
    """Представляет одно изменение в коде"""
    
    def __init__(self, action: str, entity_name: str, new_code: str, 
                 old_code: str = "", file_path: str = "", node_type: str = ""):
        self.action = action  # 'add', 'replace', 'delete', 'conflict'
        self.entity_name = entity_name
        self.new_code = new_code
        self.old_code = old_code
        self.file_path = file_path
        self.node_type = node_type
        self.conflict_reason = ""


class PendingChange:
    """Представляет отложенное изменение"""
    
    def __init__(self, action: str, entity_name: str, new_code: str = "", 
                 old_code: str = "", file_path: str = "", node_type: str = ""):
        self.action = action
        self.entity_name = entity_name
        self.new_code = new_code
        self.old_code = old_code
        self.file_path = file_path
        self.node_type = node_type
        self.timestamp = time.time()
        self.applied = False
    
    def to_code_change(self) -> CodeChange:
        """Конвертирует в обычный CodeChange"""
        return CodeChange(
            action=self.action,
            entity_name=self.entity_name,
            new_code=self.new_code,
            old_code=self.old_code,
            file_path=self.file_path,
            node_type=self.node_type
        )


class ChangeManager:
    """Управляет отложенными изменениями"""
    
    def __init__(self):
        self.pending_changes: List[PendingChange] = []
    
    def add_change(self, change: PendingChange):
        """Добавляет изменение в очередь"""
        self.pending_changes.append(change)
        logger.debug(f"Добавлено отложенное изменение: {change.action} {change.entity_name}")
    
    def get_pending_changes(self) -> List[PendingChange]:
        """Возвращает список отложенных изменений"""
        return self.pending_changes
    
    def clear_changes(self):
        """Очищает все отложенные изменения"""
        self.pending_changes.clear()
    
    @handle_errors(default_return=(False, []))
    def apply_all_changes(self) -> Tuple[bool, List[str]]:
        """Применяет все отложенные изменения"""
        if not self.pending_changes:
            return True, []
        
        try:
            # Здесь будет вызов кода для применения изменений
            # Временная реализация
            applied_count = len(self.pending_changes)
            for change in self.pending_changes:
                change.applied = True
            
            self.clear_changes()
            logger.info(f"Применено изменений: {applied_count}")
            return True, [f"Применено изменений: {applied_count}"]
            
        except Exception as e:
            logger.error(f"Ошибка при применении изменений: {e}")
            return False, [f"Ошибка: {e}"]