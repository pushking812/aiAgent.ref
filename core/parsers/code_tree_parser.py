# core/parsers/code_tree_parser.py

import logging
from pathlib import Path
from typing import Dict, Optional
from core.models.code_model import CodeNode
from core.business.ast_service import ASTService

logger = logging.getLogger('CodeTreeParser')


class CodeTreeParser:
    """
    Адаптер для обратной совместимости со старым кодом.
    Использует унифицированный ASTService внутри.
    """

    def __init__(self):
        self.ast_service = ASTService()
        logger.debug("Инициализирован CodeTreeParser (адаптер)")

    def parse_project(self, project_path: str) -> Dict[str, CodeNode]:
        """
        Парсит всю директорию проекта и возвращает дерево модулей.
        Использует унифицированный ASTService.
        """
        logger.info(f"Парсинг проекта через адаптер: {project_path}")
        return self.ast_service.parse_project(project_path)

    def parse_module(self, file_path: str) -> Optional[CodeNode]:
        """
        Парсит один исходный .py файл в иерархию CodeNode.
        Использует унифицированный ASTService.
        """
        logger.info(f"Парсинг модуля через адаптер: {file_path}")
        return self.ast_service.parse_module(file_path)
