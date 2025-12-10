# core/business/ai_schema_service.py

import re
import logging
from typing import Dict, Any, Optional
from .error_handler import handle_errors

logger = logging.getLogger('ai_code_assistant')


class AISchemaService:
    """
    Унифицированный сервис для парсинга AI-схем проекта.
    Объединяет функционал из нескольких источников в один класс.
    """
    
    @staticmethod
    @handle_errors(default_return=None)
    def parse_ai_schema(schema_text: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг текстовой AI-схемы в структурированный dict.
        Возвращает структуру: {'modules': [...], 'files': {file: content}}
        """
        logger.info(f"Парсинг AI схемы: {len(schema_text)} символов")
        
        modules = []
        files = {}
        
        try:
            # Парсим раздел modules (список путей)
            mod_match = re.search(r'modules:\s*([\s\S]+?)(files\:|$)', schema_text)
            if mod_match:
                mods_block = mod_match.group(1)
                lines = [line.strip('- ').strip() for line in mods_block.splitlines() if line.strip()]
                for line in lines:
                    if line and not line.startswith('files:') and line != '':
                        modules.append(line)
            
            # Парсим раздел files (каждая строка: file.py: "content")
            files_match = re.search(r'files:\s*([\s\S]+)', schema_text)
            if files_match:
                files_block = files_match.group(1)
                lines = [line.strip() for line in files_block.splitlines() if line.strip()]
                for line in lines:
                    # Формат: path: "content"
                    if ':' in line:
                        file_path, content = line.split(':', 1)
                        # Удалить кавычки, если есть
                        content = content.strip().strip('"').strip("'")
                        files[file_path.strip()] = content
            
            # Дополнительно парсим простую схему (старая логика)
            if not modules and not files:
                lines = schema_text.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.endswith('.py'):
                        files[line] = AISchemaService._get_default_file_content(line)
                    elif '/' in line or '\\' in line:
                        modules.append(line)
            
            result = {
                'name': 'ai_generated_project',
                'modules': modules,
                'files': files,
                'directories': []
            }
            
            logger.info(f"Схема распарсена: {len(modules)} модулей, {len(files)} файлов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге AI схемы: {e}")
            return None
    
    @staticmethod
    def _get_default_file_content(filename: str) -> str:
        """Возвращает содержимое по умолчанию для файла"""
        if filename.endswith('.py'):
            if filename == '__init__.py':
                return '# Package initialization\n'
            else:
                module_name = filename[:-3]
                return f'''"""
{module_name} - описание модуля
"""

def main():
    """Основная функция модуля"""
    print("Модуль {module_name} запущен")


if __name__ == "__main__":
    main()
'''
        elif filename == 'README.md':
            return '# Project\n\nDescription\n'
        elif filename == 'requirements.txt':
            return '# Project dependencies\n'
        else:
            return f'# {filename}\n'