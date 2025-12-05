from pathlib import Path
from typing import Dict, Optional, List
import ast
import logging

from core.models.code_model import CodeNode

logger = logging.getLogger('CodeTreeParser')


class CodeTreeParser:
    """
    Содержит бизнес-логику для парсинга Python-проекта/файла и построения структуры CodeNode.
    """

    def parse_project(self, project_path: str) -> Dict[str, CodeNode]:
        """
        Парсит всю директорию проекта и возвращает дерево модулей.
        """
        result = {}
        python_files = list(Path(project_path).rglob('*.py'))
        for file_path in python_files:
            module_node = self.parse_module(str(file_path))
            if module_node:
                result[str(file_path)] = module_node
        logger.info(f"Проект: найдено {len(result)} модулей из {len(python_files)} файлов.")
        return result

    def parse_module(self, file_path: str) -> Optional[CodeNode]:
        """
        Парсит один исходный .py файл в иерархию CodeNode.
        """
        try:
            source = Path(file_path).read_text(encoding='utf-8')
            tree = ast.parse(source, filename=file_path)
        except FileNotFoundError:
            logger.error(f'Файл не найден: {file_path}')
            return CodeNode(
                name=Path(file_path).stem,
                node_type='module_error',
                source_code=f"# Файл не найден: {file_path}",
                file_path=file_path
            )
        except (SyntaxError, Exception) as e:
            logger.error(f'Ошибка парсинга {file_path}: {e}')
            return CodeNode(
                name=Path(file_path).stem,
                node_type='module_error',
                source_code=f"# Ошибка парсинга: {str(e)}\n{source}" if 'source' in locals() else "",
                file_path=file_path
            )

        module_node = CodeNode(
            name=Path(file_path).stem,
            node_type='module',
            source_code=source,
            file_path=file_path
        )
        lines = source.split('\n')

        # Импорты (секции)
        import_lines: List[str] = []
        for item in tree.body:
            if isinstance(item, (ast.Import, ast.ImportFrom)):
                start = item.lineno - 1
                end = getattr(item, 'end_lineno', start) - 1
                import_lines.extend(lines[start:end+1])
        if import_lines:
            module_node.add_child(CodeNode(
                name='imports',
                node_type='import_section',
                source_code='\n'.join(import_lines),
                file_path=file_path
            ))

        # Классы и функции
        for item in tree.body:
            if isinstance(item, ast.ClassDef):
                class_node = self._parse_class(item, lines, file_path)
                module_node.add_child(class_node)
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_node = self._parse_function(item, lines, file_path)
                module_node.add_child(func_node)
            # Можно добавить обработку других секций (assignments, global code...)

        return module_node

    def _parse_function(self, node: ast.AST, lines: List[str], file_path: str) -> CodeNode:
        start = node.lineno - 1
        end = getattr(node, 'end_lineno', start) - 1 if hasattr(node, 'end_lineno') else start
        func_src = '\n'.join(lines[start:end+1])
        node_type = 'function' if isinstance(node, ast.FunctionDef) else 'async_function'
        return CodeNode(
            name=node.name,
            node_type=node_type,
            ast_node=node,
            source_code=func_src,
            file_path=file_path
        )

    def _parse_class(self, node: ast.ClassDef, lines: List[str], file_path: str) -> CodeNode:
        start = node.lineno - 1
        end = getattr(node, 'end_lineno', start) - 1 if hasattr(node, 'end_lineno') else start
        class_src = '\n'.join(lines[start:end+1])
        class_node = CodeNode(
            name=node.name,
            node_type='class',
            ast_node=node,
            source_code=class_src,
            file_path=file_path
        )
        # Методы класса
        for subitem in node.body:
            if isinstance(subitem, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_node = self._parse_function(subitem, lines, file_path)
                class_node.add_child(method_node)
        return class_node