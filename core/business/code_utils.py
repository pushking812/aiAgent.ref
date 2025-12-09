# core/business/code_utils.py

import re
from typing import List, Tuple


class CodeUtils:
    """Утилиты для обработки кода"""
    
    @staticmethod
    def extract_function_signature(code: str) -> Tuple[str, List[str]]:
        """Извлекает сигнатуру функции и список параметров"""
        pattern = r'^(async\s+)?def\s+(\w+)\s*\((.*?)\)\s*(->\s*[\w\[\],\s]+)?:'
        match = re.search(pattern, code.strip(), re.MULTILINE | re.DOTALL)
        
        if not match:
            return "", []
        
        func_name = match.group(2)
        params_str = match.group(3)
        
        params = []
        if params_str:
            param_pattern = r'(\w+)(?:\s*:\s*\w+)?(?:\s*=\s*[^,]+)?'
            params = re.findall(param_pattern, params_str)
        
        return func_name, params
    
    @staticmethod
    def normalize_code_indentation(code: str, spaces_per_tab: int = 4) -> str:
        """Нормализует отступы в коде"""
        lines = code.split('\n')
        normalized_lines = []
        
        for line in lines:
            if '\t' in line:
                leading_tabs = len(line) - len(line.lstrip('\t'))
                spaces = ' ' * (leading_tabs * spaces_per_tab)
                normalized_line = spaces + line.lstrip('\t')
                normalized_lines.append(normalized_line)
            else:
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)