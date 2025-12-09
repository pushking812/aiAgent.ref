# core/business/diff_engine.py

import difflib
from typing import List, Tuple
from .error_handler import handle_errors

import logging
logger = logging.getLogger('ai_code_assistant')


class DiffEngine:
    """Движок для сравнения кода и генерации diff"""
    
    @staticmethod
    @handle_errors(default_return=[])
    def generate_diff(old_code: str, new_code: str) -> List[Tuple[str, str]]:
        """Генерирует различия между старым и новым кодом"""
        logger.debug(f"Генерация diff: old={len(old_code)}, new={len(new_code)}")
        
        diff = []
        old_lines = old_code.splitlines(keepends=True)
        new_lines = new_code.splitlines(keepends=True)
        
        differ = difflib.Differ()
        diff_result = list(differ.compare(old_lines, new_lines))
        
        for line in diff_result:
            if line.startswith('  '):
                diff.append(('equal', line[2:]))
            elif line.startswith('+ '):
                diff.append(('insert', line[2:]))
            elif line.startswith('- '):
                diff.append(('delete', line[2:]))
        
        logger.debug(f"Diff сгенерирован: {len(diff)} строк")
        return diff
    
    @staticmethod
    @handle_errors(default_return="")
    def format_diff_for_display(diff: List[Tuple[str, str]]) -> str:
        """Форматирует diff для отображения в GUI"""
        result = []
        
        for change_type, line in diff:
            if change_type == 'equal':
                result.append(f"  {line}")
            elif change_type == 'insert':
                result.append(f"+ {line}")
            elif change_type == 'delete':
                result.append(f"- {line}")
        
        return ''.join(result)
    
    @staticmethod
    def has_changes(diff: List[Tuple[str, str]]) -> bool:
        """Проверяет, есть ли реальные изменения в diff"""
        return any(change_type in ('insert', 'delete') 
                  for change_type, _ in diff)