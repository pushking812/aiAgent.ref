# core/models/code_model.py

class CodeNode:
    """
    Узел AST (абстрактного синтаксического дерева) либо логической структуры кода.
    Можно расширять под свои нужды (методы, классы, функции, импорт-секции).
    """
    def __init__(self, name: str, node_type: str, source_code: str = "", 
                 children=None, parent=None, ast_node=None, file_path: str = None):
        self.name = name
        self.type = node_type           # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: используем type вместо node_type
        self.source_code = source_code
        self.children = children or []  # Инициализируем пустой список если None
        self.parent = parent
        self.ast_node = ast_node        # Оригинальный AST узел (опционально)
        self.file_path = file_path      # Путь к файлу (опционально)
        
        # Для обратной совместимости с кодом, который может ожидать ast_node
        if ast_node is not None and not hasattr(self, 'ast_node'):
            self.ast_node = ast_node

    def add_child(self, child_node):
        """Добавляет дочерний узел."""
        self.children.append(child_node)
        child_node.parent = self

    def find_child(self, name: str, node_type: str = None):
        """Находит дочерний узел по имени и (опционально) типу."""
        for child in self.children:
            if child.name == name and (node_type is None or child.type == node_type):
                return child
        return None

    def __repr__(self):
        return f"CodeNode(name={self.name}, type={self.type}, children={len(self.children)})"
    
    def to_dict(self):
        """Преобразует узел в словарь для отладки."""
        return {
            'name': self.name,
            'type': self.type,
            'children_count': len(self.children),
            'file_path': self.file_path,
            'source_code_length': len(self.source_code) if self.source_code else 0
        }