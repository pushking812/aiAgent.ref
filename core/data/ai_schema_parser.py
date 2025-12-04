# core/data/ai_schema_parser.py

import re

class AISchemaParser:
    """
    Класс для парсинга AI-схемы проекта (например, структуры по описанию от модели).
    Пример ожидаемого входного формата:
        modules:
            - utils/
            - data/
        files:
            utils/helpers.py: "# helpers content"
            data/model.py: "# model code"
    Преобразует текст-схему в dict: {'modules': [...], 'files': {path: content}}
    """

    def parse(self, schema: str):
        """
        Парсинг текстовой AI-схемы в структурированный dict.
        Возвращает структуру: {'modules': [...], 'files': {file: content}}
        """
        modules = []
        files = {}

        # Парсим раздел modules (список путей)
        mod_match = re.search(r'modules:\s*([\s\S]+?)(files\:|$)', schema)
        if mod_match:
            mods_block = mod_match.group(1)
            lines = [line.strip('- ').strip() for line in mods_block.splitlines() if line.strip()]
            for line in lines:
                if line and not line.startswith('files:') and line != '':
                    modules.append(line)

        # Парсим раздел files (каждая строка: file.py: "content")
        files_match = re.search(r'files:\s*([\s\S]+)', schema)
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

        return {'modules': modules, 'files': files}