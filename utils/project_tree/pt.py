import ast
import json
import os
import sys
from typing import Dict, List, Any, Optional, Union
import argparse
import traceback


class CodeTreeBuilder:
    def __init__(self):
        self.tree = {}

    def analyze_module(self, file_path: str) -> Dict[str, Any]:
        """Анализирует модуль и строит детализированное дерево"""
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            tree = ast.parse(content)

            # Строим полное дерево модуля
            module_tree = self._build_module_tree(tree, module_name, file_path)
            return module_tree

        except Exception as e:
            print(f"⚠️  Ошибка в {file_path}: {str(e)}")
            return {
                "name": module_name,
                "type": "module",
                "path": file_path,
                "error": str(e),
                "children": self._create_empty_module_children(),
            }

    def _create_empty_module_children(self) -> Dict[str, Any]:
        """Создает структуру детей модуля по умолчанию"""
        return {
            "imports": {"type": "imports_section", "children": {}},
            "module_variables": {"type": "module_variables_section", "children": {}},
            "global_code": {"type": "global_code_section", "children": {}},
            "functions": {"type": "functions_section", "children": {}},
            "classes": {"type": "classes_section", "children": {}},
        }

    def _create_empty_class_children(self) -> Dict[str, Any]:
        """Создает структуру детей класса по умолчанию"""
        return {
            "class_variables": {"type": "class_variables_section", "children": {}},
            "class_methods": {"type": "class_methods_section", "children": {}},
            "instance_methods": {"type": "instance_methods_section", "children": {}},
            "static_methods": {"type": "static_methods_section", "children": {}},
            "properties": {"type": "properties_section", "children": {}},
            "nested_classes": {"type": "nested_classes_section", "children": {}},
        }

    def _build_module_tree(
        self, tree: ast.Module, module_name: str, file_path: str
    ) -> Dict[str, Any]:
        """Строит дерево модуля с детализированной структурой"""
        module_tree = {
            "name": module_name,
            "type": "module",
            "path": file_path,
            "docstring": ast.get_docstring(tree),
            "children": self._create_empty_module_children(),
        }

        # Собираем все элементы модуля
        imports = []
        module_vars = []
        global_code = []
        functions = []
        classes = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
            elif isinstance(node, ast.Assign):
                module_vars.extend(self._process_assignment(node))
            elif isinstance(node, ast.AnnAssign):
                module_vars.append(self._process_ann_assignment(node))
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                # Простые выражения (возможно, строки документации или принты)
                global_code.append(node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node)
            elif isinstance(node, ast.ClassDef):
                classes.append(node)
            else:
                # Любой другой код на уровне модуля
                global_code.append(node)

        # Заполняем структуру
        self._fill_imports_section(module_tree["children"]["imports"], imports)
        self._fill_module_variables_section(
            module_tree["children"]["module_variables"], module_vars
        )
        self._fill_global_code_section(
            module_tree["children"]["global_code"], global_code
        )
        self._fill_functions_section(module_tree["children"]["functions"], functions)
        self._fill_classes_section(module_tree["children"]["classes"], classes)

        return module_tree

    def _fill_imports_section(
        self, imports_section: Dict[str, Any], imports: List[ast.AST]
    ) -> None:
        """Заполняет раздел импортов"""
        for i, node in enumerate(imports):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_node = {
                        "name": alias.name,
                        "type": "import",
                        "alias": alias.asname,
                        "line": node.lineno,
                        "children": {},
                    }
                    imports_section["children"][f"import_{i}"] = import_node
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                for alias in node.names:
                    import_node = {
                        "name": alias.name,
                        "type": "from_import",
                        "module": module_name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "level": node.level,
                        "children": {},
                    }
                    imports_section["children"][f"from_import_{i}"] = import_node

    def _process_assignment(self, node: ast.Assign) -> List[Dict[str, Any]]:
        """Обрабатывает присваивания"""
        variables = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_info = {
                    "name": target.id,
                    "type": "variable",
                    "line": node.lineno,
                    "value_preview": self._get_value_preview(node.value),
                    "children": {},
                }
                variables.append(var_info)
            elif isinstance(target, ast.Tuple):
                # Распаковка кортежа
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        var_info = {
                            "name": elt.id,
                            "type": "variable",
                            "line": node.lineno,
                            "value_preview": "(tuple unpacking)",
                            "children": {},
                        }
                        variables.append(var_info)
        return variables

    def _process_ann_assignment(self, node: ast.AnnAssign) -> Dict[str, Any]:
        """Обрабатывает аннотированные присваивания"""
        var_info = {
            "name": node.target.id
            if isinstance(node.target, ast.Name)
            else str(node.target),
            "type": "annotated_variable",
            "line": node.lineno,
            "annotation": self._ast_to_str(node.annotation),
            "children": {},
        }
        if node.value:
            var_info["value_preview"] = self._get_value_preview(node.value)
        return var_info

    def _fill_module_variables_section(
        self, section: Dict[str, Any], variables: List[Dict[str, Any]]
    ) -> None:
        """Заполняет раздел переменных модуля"""
        for i, var in enumerate(variables):
            section["children"][f"var_{i}"] = var

    def _fill_global_code_section(
        self, section: Dict[str, Any], nodes: List[ast.AST]
    ) -> None:
        """Заполняет раздел глобального кода"""
        for i, node in enumerate(nodes):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                code_node = {
                    "name": f"expr_{i}",
                    "type": "expression",
                    "line": node.lineno,
                    "value": str(node.value.value)[:100],
                    "children": {},
                }
            else:
                code_node = {
                    "name": f"code_{i}",
                    "type": "code_block",
                    "line": node.lineno,
                    "node_type": type(node).__name__,
                    "children": {},
                }
            section["children"][f"global_code_{i}"] = code_node

    def _fill_functions_section(
        self, section: Dict[str, Any], functions: List[ast.AST]
    ) -> None:
        """Заполняет раздел функций модуля"""
        for i, func in enumerate(functions):
            func_node = self._build_function_tree(func, "module_function")
            section["children"][func.name] = func_node

    def _build_function_tree(
        self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef], func_type: str
    ) -> Dict[str, Any]:
        """Строит дерево функции с детализацией"""
        is_async = isinstance(func_node, ast.AsyncFunctionDef)
        type_name = f"async_{func_type}" if is_async else func_type

        func_tree = {
            "name": func_node.name,
            "type": type_name,
            "line": func_node.lineno,
            "docstring": ast.get_docstring(func_node),
            "decorators": [self._ast_to_str(dec) for dec in func_node.decorator_list],
            "args": self._extract_function_args(func_node),
            "returns": self._ast_to_str(func_node.returns)
            if func_node.returns
            else None,
            "children": {
                "parameters": {"type": "parameters_section", "children": {}},
                "local_variables": {"type": "local_variables_section", "children": {}},
                "body_statements": {"type": "body_statements_section", "children": {}},
                "nested_functions": {
                    "type": "nested_functions_section",
                    "children": {},
                },
                "nested_classes": {"type": "nested_classes_section", "children": {}},
            },
        }

        # Анализируем параметры
        self._analyze_function_parameters(
            func_tree["children"]["parameters"], func_node
        )

        # Анализируем тело функции
        self._analyze_function_body(func_tree, func_node)

        return func_tree

    def _analyze_function_parameters(
        self, section: Dict[str, Any], func_node: ast.FunctionDef
    ) -> None:
        """Анализирует параметры функции"""
        args = func_node.args

        # Позиционные аргументы
        for i, arg in enumerate(args.posonlyargs):
            param_node = {
                "name": arg.arg,
                "type": "posonly_parameter",
                "position": i,
                "annotation": self._ast_to_str(arg.annotation)
                if arg.annotation
                else None,
                "children": {},
            }
            section["children"][f"param_posonly_{i}"] = param_node

        # Обычные аргументы
        for i, arg in enumerate(args.args):
            param_node = {
                "name": arg.arg,
                "type": "parameter",
                "position": i,
                "annotation": self._ast_to_str(arg.annotation)
                if arg.annotation
                else None,
                "children": {},
            }
            section["children"][f"param_{i}"] = param_node

        # *args
        if args.vararg:
            param_node = {
                "name": args.vararg.arg,
                "type": "varargs_parameter",
                "annotation": self._ast_to_str(args.vararg.annotation)
                if args.vararg.annotation
                else None,
                "children": {},
            }
            section["children"]["varargs"] = param_node

        # Только keyword аргументы
        for i, arg in enumerate(args.kwonlyargs):
            param_node = {
                "name": arg.arg,
                "type": "kwonly_parameter",
                "annotation": self._ast_to_str(arg.annotation)
                if arg.annotation
                else None,
                "children": {},
            }
            section["children"][f"kw_param_{i}"] = param_node

        # **kwargs
        if args.kwarg:
            param_node = {
                "name": args.kwarg.arg,
                "type": "kwargs_parameter",
                "annotation": self._ast_to_str(args.kwarg.annotation)
                if args.kwarg.annotation
                else None,
                "children": {},
            }
            section["children"]["kwargs"] = param_node

    def _analyze_function_body(
        self, func_tree: Dict[str, Any], func_node: ast.FunctionDef
    ) -> None:
        """Анализирует тело функции"""
        local_vars = []
        statements = []
        nested_funcs = []
        nested_classes = []

        for i, node in enumerate(func_node.body):
            if isinstance(node, ast.Assign):
                local_vars.extend(self._process_assignment(node))
                statements.append({"type": "assignment", "node": node, "index": i})
            elif isinstance(node, ast.AnnAssign):
                local_vars.append(self._process_ann_assignment(node))
                statements.append({"type": "ann_assignment", "node": node, "index": i})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nested_funcs.append(node)
                statements.append(
                    {"type": "function_definition", "node": node, "index": i}
                )
            elif isinstance(node, ast.ClassDef):
                nested_classes.append(node)
                statements.append(
                    {"type": "class_definition", "node": node, "index": i}
                )
            elif isinstance(node, ast.Return):
                statements.append({"type": "return", "node": node, "index": i})
            elif isinstance(node, ast.If):
                statements.append({"type": "if_statement", "node": node, "index": i})
            elif isinstance(node, ast.For):
                statements.append({"type": "for_loop", "node": node, "index": i})
            elif isinstance(node, ast.While):
                statements.append({"type": "while_loop", "node": node, "index": i})
            else:
                statements.append({"type": "statement", "node": node, "index": i})

        # Заполняем разделы
        self._fill_local_variables_section(
            func_tree["children"]["local_variables"], local_vars
        )
        self._fill_body_statements_section(
            func_tree["children"]["body_statements"], statements
        )
        self._fill_nested_functions_section(
            func_tree["children"]["nested_functions"], nested_funcs
        )
        self._fill_nested_classes_section(
            func_tree["children"]["nested_classes"], nested_classes
        )

    def _fill_local_variables_section(
        self, section: Dict[str, Any], variables: List[Dict[str, Any]]
    ) -> None:
        """Заполняет раздел локальных переменных"""
        for i, var in enumerate(variables):
            section["children"][f"local_var_{i}"] = var

    def _fill_body_statements_section(
        self, section: Dict[str, Any], statements: List[Dict[str, Any]]
    ) -> None:
        """Заполняет раздел операторов тела функции"""
        for stmt in statements:
            node = stmt["node"]
            stmt_node = {
                "name": f"stmt_{stmt['index']}",
                "type": stmt["type"],
                "line": node.lineno,
                "children": {},
            }
            section["children"][f"statement_{stmt['index']}"] = stmt_node

    def _fill_nested_functions_section(
        self, section: Dict[str, Any], functions: List[ast.AST]
    ) -> None:
        """Заполняет раздел вложенных функций"""
        for func in functions:
            func_node = self._build_function_tree(func, "nested_function")
            section["children"][func.name] = func_node

    def _fill_nested_classes_section(
        self, section: Dict[str, Any], classes: List[ast.ClassDef]
    ) -> None:
        """Заполняет раздел вложенных классов"""
        for cls in classes:
            class_node = self._build_class_tree(cls, is_nested=True)
            section["children"][cls.name] = class_node

    def _fill_classes_section(
        self, section: Dict[str, Any], classes: List[ast.ClassDef]
    ) -> None:
        """Заполняет раздел классов модуля"""
        for cls in classes:
            class_node = self._build_class_tree(cls)
            section["children"][cls.name] = class_node

    def _build_class_tree(
        self, class_node: ast.ClassDef, is_nested: bool = False
    ) -> Dict[str, Any]:
        """Строит детализированное дерево класса"""
        class_type = "nested_class" if is_nested else "class"

        class_tree = {
            "name": class_node.name,
            "type": class_type,
            "line": class_node.lineno,
            "docstring": ast.get_docstring(class_node),
            "bases": [self._ast_to_str(base) for base in class_node.bases],
            "decorators": [self._ast_to_str(dec) for dec in class_node.decorator_list],
            "metaclass": self._get_metaclass(class_node),
            "children": self._create_empty_class_children(),
        }

        # Анализируем содержимое класса
        class_vars = []
        class_methods = []
        instance_methods = []
        static_methods = []
        properties = []
        nested_classes = []

        for node in class_node.body:
            if isinstance(node, ast.Assign):
                # Переменные класса
                class_vars.extend(self._process_assignment(node))
            elif isinstance(node, ast.AnnAssign):
                class_vars.append(self._process_ann_assignment(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Определяем тип метода
                method_type = self._determine_method_type(node)
                if method_type == "classmethod":
                    class_methods.append(node)
                elif method_type == "staticmethod":
                    static_methods.append(node)
                elif method_type == "property":
                    properties.append(node)
                else:
                    instance_methods.append(node)
            elif isinstance(node, ast.ClassDef):
                nested_classes.append(node)

        # Заполняем разделы
        self._fill_class_variables_section(
            class_tree["children"]["class_variables"], class_vars
        )
        self._fill_methods_section(
            class_tree["children"]["class_methods"], class_methods, "class_method"
        )
        self._fill_methods_section(
            class_tree["children"]["instance_methods"],
            instance_methods,
            "instance_method",
        )
        self._fill_methods_section(
            class_tree["children"]["static_methods"], static_methods, "static_method"
        )
        self._fill_properties_section(class_tree["children"]["properties"], properties)
        self._fill_nested_classes_in_class_section(
            class_tree["children"]["nested_classes"], nested_classes
        )

        return class_tree

    def _determine_method_type(self, func_node: ast.FunctionDef) -> str:
        """Определяет тип метода класса"""
        decorators = [self._ast_to_str(dec) for dec in func_node.decorator_list]

        if any("classmethod" in d or d == "classmethod" for d in decorators):
            return "classmethod"
        elif any("staticmethod" in d or d == "staticmethod" for d in decorators):
            return "staticmethod"
        elif any(
            "property" in d or d in ["property", "cached_property"] for d in decorators
        ):
            return "property"
        elif any("setter" in d or "deleter" in d for d in decorators):
            return "property"
        else:
            return "instance"

    def _get_metaclass(self, class_node: ast.ClassDef) -> Optional[str]:
        """Получает метакласс из аргументов класса"""
        for keyword in class_node.keywords:
            if keyword.arg == "metaclass":
                return self._ast_to_str(keyword.value)
        return None

    def _fill_class_variables_section(
        self, section: Dict[str, Any], variables: List[Dict[str, Any]]
    ) -> None:
        """Заполняет раздел переменных класса"""
        for i, var in enumerate(variables):
            section["children"][f"class_var_{i}"] = var

    def _fill_methods_section(
        self, section: Dict[str, Any], methods: List[ast.AST], method_type: str
    ) -> None:
        """Заполняет раздел методов"""
        for method in methods:
            method_node = self._build_function_tree(method, method_type)
            section["children"][method.name] = method_node

    def _fill_properties_section(
        self, section: Dict[str, Any], properties: List[ast.AST]
    ) -> None:
        """Заполняет раздел свойств"""
        for prop in properties:
            prop_node = self._build_function_tree(prop, "property")
            section["children"][prop.name] = prop_node

    def _fill_nested_classes_in_class_section(
        self, section: Dict[str, Any], classes: List[ast.ClassDef]
    ) -> None:
        """Заполняет раздел вложенных классов внутри класса"""
        for cls in classes:
            class_node = self._build_class_tree(cls, is_nested=True)
            section["children"][cls.name] = class_node

    def _extract_function_args(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Извлекает информацию об аргументах функции"""
        args = func_node.args
        return {
            "arg_names": [arg.arg for arg in args.args],
            "defaults_count": len(args.defaults),
            "has_varargs": args.vararg is not None,
            "has_kwargs": args.kwarg is not None,
            "kwonly_args": [arg.arg for arg in args.kwonlyargs],
        }

    def _get_value_preview(self, value_node: ast.expr) -> str:
        """Получает предварительный просмотр значения"""
        try:
            if isinstance(value_node, ast.Constant):
                val = str(value_node.value)
                return val[:50] + "..." if len(val) > 50 else val
            elif isinstance(value_node, ast.Name):
                return f"Name({value_node.id})"
            elif isinstance(value_node, ast.Call):
                return "Call(...)"
            elif isinstance(value_node, ast.List):
                return "List[...]"
            elif isinstance(value_node, ast.Dict):
                return "Dict{...}"
            else:
                return type(value_node).__name__
        except:
            return "?"

    def _ast_to_str(self, node: ast.AST) -> Optional[str]:
        """Преобразует AST узел в строку"""
        if node is None:
            return None
        try:
            if hasattr(ast, "unparse"):
                return ast.unparse(node)
            elif isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return f"{self._ast_to_str(node.value)}.{node.attr}"
            elif isinstance(node, ast.Constant):
                return repr(node.value)
            else:
                return ast.dump(node, indent=2)
        except:
            return str(node)


class ProjectTreeBuilder:
    def __init__(self):
        self.code_builder = CodeTreeBuilder()
        self.project_tree = {}

    def build_project_tree(
        self, root_path: str, specific_file: str = None
    ) -> Dict[str, Any]:
        """Строит дерево всего проекта или конкретного файла"""
        if specific_file:
            return self._build_specific_file_tree(specific_file)
        elif os.path.isfile(root_path) and root_path.endswith(".py"):
            return self._build_single_file_tree(root_path)
        else:
            return self._build_directory_tree(root_path)

    def _build_specific_file_tree(self, file_path: str) -> Dict[str, Any]:
        """Строит дерево для конкретного указанного файла"""
        module_tree = self.code_builder.analyze_module(file_path)

        self.project_tree = {
            "name": os.path.basename(file_path),
            "type": "project",
            "path": os.path.dirname(file_path) or ".",
            "children": {
                "modules": {
                    "type": "modules_section",
                    "children": {os.path.basename(file_path): module_tree},
                }
            },
        }

        return self.project_tree

    def _build_single_file_tree(self, file_path: str) -> Dict[str, Any]:
        """Строит дерево для одного файла (когда передан файл как корень)"""
        return self._build_specific_file_tree(file_path)

    def _build_directory_tree(self, root_path: str) -> Dict[str, Any]:
        """Строит дерево для директории"""
        project_name = os.path.basename(os.path.normpath(root_path)) or "project"

        self.project_tree = {
            "name": project_name,
            "type": "project",
            "path": root_path,
            "children": {
                "directories": {"type": "directories_section", "children": {}},
                "modules": {"type": "modules_section", "children": {}},
            },
        }

        self._process_directory(
            root_path,
            self.project_tree["children"]["directories"],
            self.project_tree["children"]["modules"],
        )

        return self.project_tree

    def _process_directory(
        self,
        dir_path: str,
        dirs_section: Dict[str, Any],
        modules_section: Dict[str, Any],
        rel_path: str = "",
    ) -> None:
        """Рекурсивно обрабатывает директорию"""
        try:
            items = os.listdir(dir_path)
        except PermissionError:
            print(f"⚠️  Нет доступа к директории: {dir_path}")
            return

        for item in sorted(items):
            item_path = os.path.join(dir_path, item)
            item_rel_path = os.path.join(rel_path, item) if rel_path else item

            # Пропускаем служебные файлы и директории
            if (
                item.startswith(".")
                or item in ["__pycache__", "venv", "env", ".git", ".idea", ".vscode"]
                or item.endswith(".pyc")
            ):
                continue

            if os.path.isdir(item_path):
                # Обрабатываем поддиректорию
                dir_node = {
                    "name": item,
                    "type": "directory",
                    "path": item_rel_path,
                    "children": {
                        "subdirectories": {
                            "type": "subdirectories_section",
                            "children": {},
                        },
                        "files": {"type": "files_section", "children": {}},
                    },
                }
                dirs_section["children"][item] = dir_node

                # Рекурсивно обрабатываем поддиректорию
                self._process_directory(
                    item_path,
                    dir_node["children"]["subdirectories"],
                    modules_section,
                    item_rel_path,
                )

            elif os.path.isfile(item_path) and item.endswith(".py"):
                # Анализируем Python файл
                module_tree = self.code_builder.analyze_module(item_path)
                modules_section["children"][
                    item_rel_path.replace(os.sep, ".")
                ] = module_tree

    def export_to_json(self, output_file: str = "project_tree.json") -> None:
        """Экспортирует дерево в JSON"""
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.project_tree, f, indent=2, ensure_ascii=False)

        print(f"✅ Дерево проекта экспортировано в: {os.path.abspath(output_file)}")

    def print_tree_summary(
        self, node: Dict = None, indent: int = 0, max_depth: int = 3
    ) -> None:
        """Выводит сводку дерева"""
        if node is None:
            node = self.project_tree

        prefix = "  " * indent

        # Иконки для разных типов
        icons = {
            "project": "📦",
            "directory": "📁",
            "module": "📄",
            "class": "🏗️",
            "function": "⚙️",
            "method": "🔧",
            "import": "📥",
            "variable": "📝",
            "section": "📑",
        }

        node_type = node.get("type", "")
        icon = icons.get(node_type, "•")

        # Выводим информацию о узле
        name = node.get("name", "")
        line_info = f" (line {node['line']})" if node.get("line") else ""

        print(f"{prefix}{icon} {name} [{node_type}]{line_info}")

        # Выводим детей, если не превышена глубина
        if indent < max_depth and node.get("children"):
            for child_name, child_node in sorted(node["children"].items()):
                self.print_tree_summary(child_node, indent + 1, max_depth)


def main():
    parser = argparse.ArgumentParser(
        description="Построитель дерева структуры Python кода с детализированной структурой",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Типы узлов в дереве:
• project - Корень проекта
• directory - Директория
• module - Python модуль
• class / nested_class - Класс / Вложенный класс
• module_function / async_module_function - Функция модуля
• instance_method / class_method / static_method - Методы класса
• property - Свойство класса
• import / from_import - Импорты
• variable / annotated_variable - Переменные
• section - Разделы (imports_section, functions_section и т.д.)

Примеры использования:
  python detailed_tree.py project/ -o detailed_tree.json
  python detailed_tree.py module.py -p -d 4
  python detailed_tree.py . --file utils/calculator.py
  python detailed_tree.py --file project/analyzer.py --output analyzer_tree.json
        """,
    )

    # Основные аргументы
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Путь к директории для анализа (по умолчанию: текущая директория)",
    )

    parser.add_argument(
        "-f",
        "--file",
        help="Анализировать конкретный файл (абсолютный или относительный путь)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Имя выходного JSON файла (по умолчанию: project_tree.json для проекта или <имя_файла>_tree.json для файла)",
    )

    parser.add_argument(
        "-p", "--print", action="store_true", help="Вывести дерево в консоль"
    )

    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=3,
        help="Глубина вывода дерева (по умолчанию: 3)",
    )

    parser.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="Вывести статистику по проекту/файлу",
    )

    parser.add_argument(
        "-r",
        "--relative",
        action="store_true",
        help="Использовать относительные пути в выводе",
    )

    args = parser.parse_args()

    # Определяем, что анализировать
    if args.file:
        # Анализируем конкретный файл
        file_path = args.file
        if not os.path.exists(file_path):
            print(f"❌ Ошибка: файл '{file_path}' не существует")
            sys.exit(1)

        if not file_path.endswith(".py"):
            print(
                f"⚠️  Предупреждение: файл '{file_path}' не является Python файлом (.py)"
            )

        # Определяем выходной файл по умолчанию
        if not args.output:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            args.output = f"{base_name}_tree.json"

        print(f"🔍 Анализирую файл: {os.path.abspath(file_path)}")

    else:
        # Анализируем директорию или файл из path
        if not os.path.exists(args.path):
            print(f"❌ Ошибка: путь '{args.path}' не существует")
            sys.exit(1)

        # Определяем выходной файл по умолчанию
        if not args.output:
            if os.path.isfile(args.path) and args.path.endswith(".py"):
                base_name = os.path.splitext(os.path.basename(args.path))[0]
                args.output = f"{base_name}_tree.json"
            else:
                args.output = "project_tree.json"

        if os.path.isfile(args.path) and args.path.endswith(".py"):
            print(f"🔍 Анализирую файл: {os.path.abspath(args.path)}")
            file_path = args.path
        else:
            print(f"📁 Анализирую директорию: {os.path.abspath(args.path)}")
            file_path = None

    # Строим дерево проекта
    builder = ProjectTreeBuilder()

    if args.file:
        project_tree = builder.build_project_tree(
            os.path.dirname(file_path) or ".", specific_file=file_path
        )
    else:
        if os.path.isfile(args.path) and args.path.endswith(".py"):
            project_tree = builder.build_project_tree(args.path)
        else:
            project_tree = builder.build_project_tree(args.path)

    if args.print:
        print("\n" + "=" * 60)

        if args.file or (os.path.isfile(args.path) and args.path.endswith(".py")):
            print(
                f"📄 ДЕРЕВО СТРУКТУРЫ ФАЙЛА: {os.path.basename(file_path or args.path)}"
            )
        else:
            print(
                f"🌳 ДЕРЕВО СТРУКТУРЫ ПРОЕКТА: {os.path.basename(args.path) or 'текущая директория'}"
            )

        print("=" * 60)
        builder.print_tree_summary(max_depth=args.depth)
        print("=" * 60)

    if args.summary:
        print_stats(project_tree)

    builder.export_to_json(args.output)


def print_stats(tree: Dict[str, Any]) -> None:
    """Выводит статистику по дереву"""
    stats = {
        "modules": 0,
        "classes": 0,
        "functions": 0,
        "methods": 0,
        "imports": 0,
        "variables": 0,
    }

    def count_nodes(node: Dict[str, Any]):
        node_type = node.get("type", "")

        if node_type == "module":
            stats["modules"] += 1
        elif node_type in ["class", "nested_class"]:
            stats["classes"] += 1
        elif "function" in node_type:
            stats["functions"] += 1
        elif "method" in node_type:
            stats["methods"] += 1
        elif node_type in ["import", "from_import"]:
            stats["imports"] += 1
        elif node_type in ["variable", "annotated_variable"]:
            stats["variables"] += 1

        if "children" in node:
            for child in node["children"].values():
                count_nodes(child)

    count_nodes(tree)

    print("\n📊 СТАТИСТИКА ПРОЕКТА:")
    print("-" * 30)
    print(f"📁 Модули: {stats['modules']}")
    print(f"🏗️  Классы: {stats['classes']}")
    print(f"⚙️  Функции: {stats['functions']}")
    print(f"🔧 Методы: {stats['methods']}")
    print(f"📥 Импорты: {stats['imports']}")
    print(f"📝 Переменные: {stats['variables']}")
    print("-" * 30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Анализ прерван пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
