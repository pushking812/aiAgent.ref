# core/models/code_model.py

class CodeNode:
    """
    Узел AST (абстрактного синтаксического дерева) либо логической структуры кода.
    Можно расширять под свои нужды (методы, классы, функции, импорт-секции).
    """
    def __init__(self, name: str, node_type: str, source_code: str = "", children=None, parent=None):
        self.name = name                # имя сущности (например, имя функции или класса)
        self.type = node_type           # тип узла ('class', 'function', 'method', 'import_section', ...)
        self.source_code = source_code  # исходный код этого узла
        self.children = children or []  # дочерние узлы (CodeNode)
        self.parent = parent            # родительский узел (CodeNode или None)

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self

    def find_child(self, name: str, node_type: str):
        for child in self.children:
            if child.name == name and child.type == node_type:
                return child
        return None

    def __repr__(self):
        return f"CodeNode(name={self.name}, type={self.type}, children={len(self.children)})"