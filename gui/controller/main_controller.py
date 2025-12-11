# gui/controller/main_controller.py

import os
import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, List

from gui.views.main_window_view import IMainWindowView
from gui.views.code_editor_view import CodeEditorView, ICodeEditorView
from gui.views.project_tree_view import IProjectTreeView
from gui.views.dialogs_view import DialogsView
from gui.views.analysis_view import AnalysisView, IAnalysisView  # Добавить AnalysisView
from core.business.project_service import IProjectService
from core.business.code_service import ICodeService
from core.business.analysis_service import IAnalysisService
from core.business.change_service import PendingChange
from core.app_context import get_app_context
from gui.utils.ui_factory import ui_factory

logger = logging.getLogger('ai_code_assistant')


class MainController:
    """
    Основной контроллер с использованием единого AppContext.
    Устраняет дублирование создания сервисов.
    """
    
    def __init__(
        self,
        main_window_view: IMainWindowView,
        code_editor_view: ICodeEditorView,
        project_tree_view: IProjectTreeView,
        dialogs_view: DialogsView,
        analysis_view: IAnalysisView,
        project_service: IProjectService,
        code_service: ICodeService,
        analysis_service: IAnalysisService,
    ):
        self.main_window_view = main_window_view
        self.code_editor_view = code_editor_view
        self.project_tree_view = project_tree_view
        self.dialogs_view = dialogs_view
        self.analysis_view = analysis_view
        self.project_service = project_service
        self.code_service = code_service
        self.analysis_service = analysis_service
        
        # Получаем сервисы из контекста вместо создания собственных
        self.app_context = get_app_context()
        
        # Получаем необходимые сервисы
        self.code_manager = self.app_context.get_code_manager()
        self.change_manager = self.app_context.get_change_manager()
        self.diff_engine = self.app_context.get_diff_engine()
        self.ast_service = self.app_context.get_ast_service()
        self.project_creator = self.app_context.get_project_creator()
        self.ai_schema_service = self.app_context.get_ai_schema_service()
        
        
        # Для обратной совместимости - получаем парсер через сервис
        from core.data.ai_schema_parser import AISchemaParser  # Локальный импорт
        self.schema_parser = AISchemaParser()
        
        # Состояние контроллера
        self.current_file_path: Optional[str] = None
        self.has_unsaved_changes = False
        self.auto_save_on_blur = False
        self.project_ast_tree: Dict[str, Any] = {}
        
        # Инициализация GUI
        self._setup_gui_structure()
        self._setup_event_bindings()
        
        logger.info("MainController инициализирован с использованием AppContext")

    def _setup_gui_structure(self):
        """Настраивает структуру GUI с использованием фабрики."""
        # Получаем панель контента из MainWindowView
        content_panel = self.main_window_view.get_content_panel()
        
        if not content_panel:
            logger.error("Не удалось получить content_panel из MainWindowView")
            return
            
        # Очищаем предыдущие виджеты если есть
        for widget in content_panel.winfo_children():
            widget.destroy()
        
        # Создаем главную область контента через фабрику
        content_frame = ui_factory.create_frame(content_panel)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - дерево проекта (фиксированная ширина 300px)
        left_panel = ui_factory.create_frame(content_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Настраиваем компоненты в левой панели через фабрику
        self._setup_left_panel_components(left_panel)
        
        # Правая панель - редакторы кода и анализ
        right_panel = ui_factory.create_frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Верхняя часть правой панели - редакторы кода
        editor_container = ui_factory.create_label_frame(right_panel, text="Редактор кода", padding=5)
        editor_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Размещаем CodeEditorView
        if hasattr(self.code_editor_view, 'pack'):
            self.code_editor_view.pack(in_=editor_container, fill=tk.BOTH, expand=True)
        else:
            # Если CodeEditorView не упакован, создаем его заново
            self.code_editor_view = CodeEditorView(editor_container)
            self.code_editor_view.pack(fill=tk.BOTH, expand=True)
        
        # Нижняя часть правой панели - анализ кода
        analysis_container = ui_factory.create_label_frame(right_panel, text="Анализ кода", padding=5)
        analysis_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Настраиваем панель анализа через фабрику
        if hasattr(self.analysis_view, 'setup_analysis_panel'):
            self.analysis_view.setup_analysis_panel(analysis_container)
        else:
            # Если AnalysisView не настроен, создаем его заново
            self.analysis_view = AnalysisView(analysis_container)
        
        logger.debug("GUI структура настроена")

    def _setup_left_panel_components(self, left_panel):
        """Настраивает компоненты левой панели через фабрику."""
        # Панель поиска
        self.project_tree_view.setup_search_panel(left_panel)
        
        # Кнопки управления деревом
        self.project_tree_view.setup_tree_buttons(left_panel)
        
        # Само дерево
        self.project_tree_view.setup_tree()
        self.project_tree_view.pack(in_=left_panel, fill=tk.BOTH, expand=True)
        
        # Дополнительные кнопки управления
        self._setup_additional_tree_buttons(left_panel)

    def _setup_additional_tree_buttons(self, parent):
        """Создает дополнительные кнопки управления деревом через фабрику."""
        extra_buttons_frame = ui_factory.create_label_frame(parent, text="Управление", padding=5)
        extra_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Конфигурация дополнительных кнопок
        extra_buttons_config = [
            {
                'text': '📊',
                'tooltip': 'Показать структуру AST',
                'square': True,
                'command': self.on_show_ast_structure
            },
            {
                'text': '🔍',
                'tooltip': 'Найти конфликты кода',
                'square': True,
                'command': self.on_find_code_conflicts
            },
            {
                'text': '📝',
                'tooltip': 'Сгенерировать документацию',
                'square': True,
                'command': self.on_generate_documentation
            },
            {
                'text': '🔄',
                'tooltip': 'Сравнить версии',
                'square': True,
                'command': self.on_compare_versions
            }
        ]
        
        # Создаем кнопки через фабрику
        for config in extra_buttons_config:
            btn = ui_factory.create_button(
                extra_buttons_frame,
                text=config['text'],
                command=config['command'],
                tooltip=config['tooltip'],
                square=config['square']
            )
            btn.pack(side=tk.LEFT, padx=2)

    def _setup_event_bindings(self):
        """Настраивает привязки событий GUI."""
        # Проект
        self.main_window_view.bind_create_project(self.on_create_project_clicked)
        self.main_window_view.bind_open_project(self.on_open_project_clicked)
        self.main_window_view.bind_create_structure(self.on_create_project_structure_from_ai)
        self.main_window_view.bind_refresh_project(self.on_refresh_project)
        self.main_window_view.bind_save_project(self.on_save_project)
        self.main_window_view.bind_show_pending_changes(self.on_show_pending_changes)
        self.main_window_view.bind_close_project(self.on_close_project)
        
        # Анализ
        self.main_window_view.bind_analyze_code(self.on_analyze_code)
        self.main_window_view.bind_show_analysis_report(self.on_show_analysis_report)
        self.main_window_view.bind_auto_refactor(self.on_auto_refactor)
        
        # Редактор
        self.main_window_view.bind_save_current_file(self.on_save_current_file)
        self.main_window_view.bind_delete_selected_element(self.on_delete_selected_element)
        
        # AI код
        self.main_window_view.bind_add_ai_code(self.on_add_ai_code)
        self.main_window_view.bind_replace_selected_element(self.on_replace_selected_element)
        self.main_window_view.bind_clear_ai_code(self.on_clear_ai_code)
        
        # Дерево проекта
        if hasattr(self.project_tree_view, 'expand_all_button'):
            self.project_tree_view.expand_all_button.config(command=self.on_expand_all)
        if hasattr(self.project_tree_view, 'collapse_all_button'):
            self.project_tree_view.collapse_all_button.config(command=self.on_collapse_all)
        if hasattr(self.project_tree_view, 'find_next_button'):
            self.project_tree_view.find_next_button.config(command=self.on_find_next)
        
        # Редактор
        self.code_editor_view.bind_on_text_modified(self.on_code_modified)
        self.code_editor_view.bind_focus_out(self.on_editor_focus_out)
        self.code_editor_view.bind_on_ai_modified(self.on_ai_modified)
        
        # Дерево проекта
        self.project_tree_view.set_on_tree_select_callback(self.on_tree_item_selected_with_code_display)
        
        # Анализ
        self.analysis_view.bind_analyze_code(self.on_analyze_code)
        self.analysis_view.bind_show_analysis_report(self.on_show_analysis_report)
        self.analysis_view.bind_auto_refactor(self.on_auto_refactor)
        
        # Настройка автосохранения
        self.auto_save_var = tk.BooleanVar(value=False)
        self.code_editor_view.setup_auto_save_checkbox(self.auto_save_var)
        self.auto_save_var.trace_add('write', self._on_auto_save_changed)
        
        logger.debug("Привязки событий настроены")

    def _on_auto_save_changed(self, *args):
        """Обработчик изменения состояния автосохранения."""
        self.auto_save_on_blur = self.auto_save_var.get()
        logger.info("Автосохранение: %s", "включено" if self.auto_save_on_blur else "выключено")

    # --- Восстановленные методы ---
    
    def on_show_ast_structure(self):
        """Показать структуру AST текущего файла."""
        if not self.current_file_path:
            self.main_window_view.show_warning("AST Структура", "Нет открытого файла")
            return
        
        try:
            # Используем AST сервис из контекста
            ast_node = self.ast_service.parse_module(self.current_file_path)
            if ast_node:
                structure_info = self._format_ast_structure(ast_node)
                self.dialogs_view.show_info_dialog("AST Структура", structure_info)
            else:
                self.main_window_view.show_error("AST Структура", "Не удалось проанализировать файл")
                
        except Exception as e:
            logger.error(f"Ошибка при анализе AST: {e}")
            self.main_window_view.show_error("AST Структура", f"Ошибка: {e}")

    def _format_ast_structure(self, ast_node) -> str:
        """Форматирует информацию о структуре AST для отображения."""
        info_lines = [f"Файл: {os.path.basename(self.current_file_path)}"]
        info_lines.append(f"Тип: {ast_node.type}")
        info_lines.append(f"Имя: {ast_node.name}")
        info_lines.append(f"Элементов: {len(ast_node.children)}")
        
        for i, child in enumerate(ast_node.children):
            info_lines.append(f"  {i+1}. {child.type}: {child.name}")
            if hasattr(child, 'children') and child.children:
                for j, grandchild in enumerate(child.children):
                    info_lines.append(f"      {j+1}. {grandchild.type}: {grandchild.name}")
        
        return "\n".join(info_lines)

    def on_find_code_conflicts(self):
        """Найти конфликты в коде."""
        if not self.current_file_path:
            self.main_window_view.show_warning("Конфликты", "Нет открытого файла")
            return
        
        ai_code = self.code_editor_view.get_ai_content()
        if not ai_code:
            self.main_window_view.show_warning("Конфликты", "Введите AI-код для анализа")
            return
        
        try:
            # Используем CodeManager из контекста
            if not self.project_ast_tree:
                self.project_ast_tree = self.ast_service.parse_project(
                    os.path.dirname(self.current_file_path)
                )
            
            from core.business.code_manager import CodeChange
            changes = self.code_manager.analyze_ai_code(
                ai_code, 
                self.project_ast_tree,
                self.current_file_path
            )
            
            # Фильтруем конфликты
            conflicts = [c for c in changes if c.action == 'conflict']
            
            if conflicts:
                conflict_info = self._format_conflicts_info(conflicts)
                self.dialogs_view.show_warning_dialog(
                    "Обнаружены конфликты", 
                    conflict_info
                )
            else:
                self.main_window_view.show_info("Конфликты", "Конфликты не обнаружены")
                
        except Exception as e:
            logger.error(f"Ошибка при поиске конфликтов: {e}")
            self.main_window_view.show_error("Конфликты", f"Ошибка: {e}")

    def _format_conflicts_info(self, conflicts) -> str:
        """Форматирует информацию о конфликтах для отображения."""
        info_lines = [f"Найдено конфликтов: {len(conflicts)}"]
        
        for i, conflict in enumerate(conflicts):
            info_lines.append(f"\n{i+1}. {conflict.entity_name} ({conflict.node_type})")
            info_lines.append(f"   Файл: {os.path.basename(conflict.file_path)}")
            info_lines.append(f"   Причина: {conflict.conflict_reason}")
            
            # Показываем превью старого и нового кода
            old_preview = conflict.old_code[:100].replace('\n', ' ') + '...' if len(conflict.old_code) > 100 else conflict.old_code
            new_preview = conflict.new_code[:100].replace('\n', ' ') + '...' if len(conflict.new_code) > 100 else conflict.new_code
            
            info_lines.append(f"   Старый код: {old_preview}")
            info_lines.append(f"   Новый код: {new_preview}")
        
        return "\n".join(info_lines)

    def on_generate_documentation(self):
        """Сгенерировать документацию для текущего файла."""
        if not self.current_file_path:
            self.main_window_view.show_warning("Документация", "Нет открытого файла")
            return
        
        try:
            # Используем AST сервис из контекста
            ast_node = self.ast_service.parse_module(self.current_file_path)
            if ast_node:
                documentation = self._generate_documentation(ast_node)
                self.dialogs_view.show_info_dialog(
                    "Сгенерированная документация", 
                    documentation
                )
            else:
                self.main_window_view.show_error("Документация", "Не удалось проанализировать файл")
                
        except Exception as e:
            logger.error(f"Ошибка при генерации документации: {e}")
            self.main_window_view.show_error("Документация", f"Ошибка: {e}")

    def _generate_documentation(self, ast_node) -> str:
        """Генерирует документацию на основе AST."""
        doc_lines = [f"# Документация для {os.path.basename(self.current_file_path)}"]
        doc_lines.append(f"\n## Описание файла")
        doc_lines.append(f"Файл содержит {len(ast_node.children)} основных элементов.\n")
        
        for i, child in enumerate(ast_node.children):
            if child.type in ['class', 'function', 'async_function', 'method']:
                doc_lines.append(f"### {child.type.capitalize()}: {child.name}")
                
                # Извлекаем докстринг если есть
                lines = child.source_code.split('\n')
                for line in lines:
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        doc_lines.append(f"\n{line.strip()}")
                        break
                
                # Добавляем информацию о аргументах для функций
                if child.type in ['function', 'async_function', 'method']:
                    doc_lines.append(f"\n**Параметры:** TODO")  # Можно расширить
                
                doc_lines.append("")
        
        return "\n".join(doc_lines)

    def on_compare_versions(self):
        """Сравнить версии файла."""
        if not self.current_file_path:
            self.main_window_view.show_warning("Сравнение", "Нет открытого файла")
            return
        
        try:
            # Получаем текущее содержимое
            current_content = self.code_editor_view.get_source_content()
            
            # Получаем сохраненное содержимое из файловой системы
            saved_content = self.code_service.get_file_content(self.current_file_path)
            
            if current_content == saved_content:
                self.main_window_view.show_info("Сравнение", "Файлы идентичны")
                return
            
            # Используем DiffEngine из контекста
            diff = self.diff_engine.generate_diff(saved_content, current_content)
            
            if self.diff_engine.has_changes(diff):
                formatted_diff = self.diff_engine.format_diff_for_display(diff)
                self.dialogs_view.show_diff(
                    formatted_diff, 
                    title=f"Сравнение: {os.path.basename(self.current_file_path)}"
                )
            else:
                self.main_window_view.show_info("Сравнение", "Нет различий")
                
        except Exception as e:
            logger.error(f"Ошибка при сравнении версий: {e}")
            self.main_window_view.show_error("Сравнение", f"Ошибка: {e}")

    # --- Обработчики событий проекта ---
    
    def on_create_project_clicked(self):
        """Обработка создания нового проекта."""
        result = self.dialogs_view.show_project_creation_dialog(self.project_service)
        
        if result:
            path, name, template_name, is_empty, full_path = result
            
            # Используем ProjectCreatorService из контекста
            if is_empty:
                success = self.project_creator.create_basic_python_project(path, name)
            else:
                success = self.project_creator.create_project_from_template(
                    template_name, path, name
                )
            
            if success:
                self.main_window_view.set_status(f"Проект создан: {name}")
                self.main_window_view.show_info("Успех", "Проект успешно создан!")
                
                # Открываем созданный проект
                self.project_service.open_project(full_path)
                self._load_project_tree()
            else:
                self.main_window_view.show_error("Ошибка", "Не удалось создать проект!")

    def on_open_project_clicked(self):
        """Обработка открытия существующего проекта."""
        directory = self.dialogs_view.ask_directory("Выберите директорию проекта")
        
        if directory:
            success = self.project_service.open_project(directory)
            if success:
                self.main_window_view.set_status(f"Открыт проект: {directory}")
                
                # Загружаем дерево проекта с AST данными
                self.project_tree_view.load_project_from_repository(self.project_service)
                
                self._update_ast_tree(directory)
            else:
                self.main_window_view.show_error("Ошибка", "Не удалось открыть проект!")

    def _update_ast_tree(self, project_path: str):
        """Обновляет AST дерево проекта."""
        try:
            self.project_ast_tree = self.ast_service.parse_project(project_path)
            logger.info(f"AST дерево обновлено: {len(self.project_ast_tree)} модулей")
        except Exception as e:
            logger.error(f"Ошибка при обновлении AST дерева: {e}")

    def on_create_project_structure_from_ai(self):
        """Генерация структуры проекта по AI-схеме."""
        ai_code = self.code_editor_view.get_ai_content()
        if not ai_code:
            self.main_window_view.show_warning("AI Схема", "Введите AI-схему!")
            return
        
        # Используем AISchemaService из контекста
        structure = self.ai_schema_service.parse_ai_schema(ai_code)
        if not structure:
            self.main_window_view.show_error("Ошибка", "Не удалось распарсить AI схему")
            return
        
        if not self.project_service.project_path:
            # Создаем новый проект из схемы
            result = self.dialogs_view.show_project_creation_dialog(self.project_service)
            if result:
                path, name, _, _, full_path = result
                success = self.project_creator.create_project_from_ai_schema(
                    structure, full_path
                )
                if success:
                    self.project_service.open_project(full_path)
                    self._load_project_tree()
        else:
            # Добавляем структуру в существующий проект
            success = self.project_creator.create_project_from_ai_schema(
                structure, self.project_service.project_path
            )
            if success:
                self.main_window_view.show_info("Структура проекта", "Структура успешно добавлена!")
                self._load_project_tree()
            else:
                self.main_window_view.show_error("Ошибка", "Ошибка добавления структуры!")

    def on_refresh_project(self):
        """Обновить проект."""
        if self.project_service.project_path:
            self._load_project_tree()
            self._update_ast_tree(self.project_service.project_path)
            self.main_window_view.set_status("Проект обновлен")
        else:
            self.main_window_view.show_warning("Обновение", "Нет открытого проекта")

    def on_save_project(self):
        """Сохранить весь проект."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Сохранение", "Нет открытого проекта")
            return
        
        # Сохранить текущий файл если есть изменения
        if self.has_unsaved_changes and self.current_file_path:
            self.on_save_current_file()
        
        # Применить отложенные изменения через ChangeManager из контекста
        pending_changes = self.change_manager.get_pending_changes()
        if pending_changes:
            success, messages = self.change_manager.apply_all_changes()
            if success:
                self.main_window_view.show_info("Изменения", "Отложенные изменения применены")
            else:
                self.main_window_view.show_error("Изменения", "Ошибка применения изменений")
        
        self.main_window_view.show_info("Сохранение", "Проект сохранен")
        self.main_window_view.set_status("Проект сохранен")

    def on_show_pending_changes(self):
        """Показать отложенные изменения."""
        pending_changes = self.change_manager.get_pending_changes()
        if not pending_changes:
            self.main_window_view.show_info("Отложенные изменения", "Нет отложенных изменений")
            return
        
        # Показываем диалог с отложенными изменениями
        apply_changes = self.dialogs_view.show_pending_changes_dialog(pending_changes)
        
        if apply_changes:
            success, messages = self.change_manager.apply_all_changes()
            if success:
                self.main_window_view.show_info("Изменения", "Отложенные изменения применены")
                self._load_project_tree()  # Обновляем дерево
            else:
                self.main_window_view.show_error("Изменения", "Ошибка применения изменений")
        else:
            self.change_manager.clear_changes()
            self.main_window_view.show_info("Изменения", "Отложенные изменения отменены")

    def on_close_project(self):
        """Закрыть проект."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Закрытие", "Нет открытого проекта")
            return
        
        # Проверяем несохраненные изменения
        if self.has_unsaved_changes or self.change_manager.get_pending_changes():
            response = self.dialogs_view.ask_save_changes("проект")
            
            if response is None:  # Отмена
                return
            elif response:  # Сохранить
                self.on_save_project()
        
        success = self.project_service.close_project()
        if success:
            self.main_window_view.set_status("Проект закрыт")
            self._clear_all_views()
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось закрыть проект")

    # --- Обработчики событий анализа ---
    
    def on_analyze_code(self):
        """Анализировать код проекта."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Анализ", "Сначала откройте проект")
            return
        
        self.analysis_view.clear_analysis()
        self.analysis_view.add_analysis_result("info", "Начало анализа проекта")
        
        try:
            analysis_results = self.analysis_service.analyze_code(self.project_service.project_path)
            
            for result in analysis_results:
                self.analysis_view.add_analysis_result(
                    result.get('type', 'info'),
                    result.get('message', ''),
                    result.get('file', ''),
                    result.get('line', 0)
                )
            
            self.analysis_view.add_analysis_result("success", "Анализ завершен")
            self.main_window_view.show_info("Анализ", "Анализ проекта завершен")
            
        except Exception as e:
            logger.error("Ошибка анализа: %s", e)
            self.analysis_view.add_analysis_result("error", f"Ошибка анализа: {e}")
            self.main_window_view.show_error("Анализ", f"Ошибка анализа: {e}")

    def on_show_analysis_report(self):
        """Показать отчет анализа."""
        self.analysis_view.show_analysis_report()

    def on_auto_refactor(self):
        """Авторефакторинг кода."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Рефакторинг", "Сначала откройте проект")
            return
        
        self.main_window_view.show_info("Рефакторинг", "Авторефакторинг запущен")
        
        try:
            success = self.analysis_service.auto_refactor(self.project_service.project_path)
            
            if success:
                self.main_window_view.show_info("Рефакторинг", "Авторефакторинг завершен")
                self._load_project_tree()
                self._update_ast_tree(self.project_service.project_path)
            else:
                self.main_window_view.show_error("Рефакторинг", "Ошибка рефакторинга")
                
        except Exception as e:
            logger.error("Ошибка рефакторинга: %s", e)
            self.main_window_view.show_error("Рефакторинг", f"Ошибка рефакторинга: {e}")

    # --- Обработчики событий редактора ---
    
    def on_code_modified(self, event=None):
        """Автосохранение при изменении кода."""
        if not self.current_file_path:
            return
        
        self.has_unsaved_changes = True
        self.code_editor_view.update_modified_status(True)
        self._update_unsaved_changes_status()
        
        # Автосохранение если включено
        if self.auto_save_on_blur:
            logger.info("Выполняется автосохранение")
            self.on_save_current_file()

    def on_ai_modified(self, event=None):
        """Обработка изменения AI-кода."""
        ai_code = self.code_editor_view.get_ai_content()
        if ai_code:
            self.main_window_view.set_status(f"AI-код: {len(ai_code)} символов")
            
            # Автоматический анализ AI-кода на конфликты
            if self.current_file_path and self.project_ast_tree:
                try:
                    changes = self.code_manager.analyze_ai_code(
                        ai_code, 
                        self.project_ast_tree,
                        self.current_file_path
                    )
                    
                    conflicts = [c for c in changes if c.action == 'conflict']
                    if conflicts:
                        self.main_window_view.set_status(
                            f"Обнаружено {len(conflicts)} конфликтов в AI-коде"
                        )
                except Exception as e:
                    logger.debug(f"Ошибка при анализе AI-кода: {e}")

    def on_editor_focus_out(self, event=None):
        """Обработчик потери фокуса редактором (автосохранение)."""
        if self.auto_save_on_blur and self.has_unsaved_changes and self.current_file_path:
            logger.info("Автосохранение при потере фокуса для файла: %s", self.current_file_path)
            self.on_save_current_file()

    def on_save_current_file(self):
        """Сохранить текущий файл."""
        if not self.current_file_path:
            self.main_window_view.show_warning("Сохранение", "Нет открытого файла")
            return
        
        content = self.code_editor_view.get_source_content()
        success = self.code_service.save_current_file(content)
        
        if success:
            self.has_unsaved_changes = False
            self.code_editor_view.update_modified_status(False)
            self._update_unsaved_changes_status()
            self.main_window_view.set_status("Файл сохранен")
            
            # Обновляем AST дерево
            if self.project_service.project_path:
                self._update_ast_tree(self.project_service.project_path)
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось сохранить файл")

    def on_delete_selected_element(self):
        """Удалить выбранный элемент."""
        selected_item = self.project_tree_view.get_selected_item()
        if not selected_item:
            self.main_window_view.show_warning("Удаление", "Выберите элемент для удаления")
            return
        
        # Подтверждение удаления
        result = self.dialogs_view.show_warning_dialog(
            "Удаление",
            f"Вы уверены, что хотите удалить элемент '{selected_item.get('clean_name', selected_item.get('name'))}'?"
        )
        
        if result:
            # Создаем отложенное изменение через ChangeManager
            pending_change = PendingChange(
                action='delete',
                entity_name=selected_item.get('clean_name', selected_item.get('name')),
                file_path=selected_item.get('path'),
                node_type=selected_item.get('type')
            )
            
            self.change_manager.add_change(pending_change)
            self._update_unsaved_changes_status()
            
            self.main_window_view.show_info("Удаление", "Элемент помещен в очередь удаления")
            self.main_window_view.set_status("Элемент будет удален при сохранении проекта")

    # --- Обработчики событий AI кода ---
    
    def on_add_ai_code(self):
        """Добавить AI код в проект."""
        ai_code = self.code_editor_view.get_ai_content()
        if not ai_code:
            self.main_window_view.show_warning("AI Код", "Введите код в поле AI")
            return
        
        selected_item = self.project_tree_view.get_selected_item()
        if not selected_item:
            self.main_window_view.show_warning("AI Код", "Выберите место для добавления кода")
            return
        
        # Анализируем AI-код перед добавлением
        changes = []
        if self.project_ast_tree:
            changes = self.code_manager.analyze_ai_code(
                ai_code, 
                self.project_ast_tree,
                selected_item.get('path')
            )
        
        # Если есть конфликты, показываем предупреждение
        conflicts = [c for c in changes if c.action == 'conflict']
        if conflicts:
            response = self.dialogs_view.show_warning_dialog(
                "Конфликты обнаружены",
                f"Найдено {len(conflicts)} конфликтов. Все равно добавить код?"
            )
            if not response:
                return
        
        # Создаем отложенное изменение
        pending_change = PendingChange(
            action='add',
            entity_name='AI код',
            new_code=ai_code,
            file_path=selected_item.get('path'),
            node_type='ai_code'
        )
        
        self.change_manager.add_change(pending_change)
        self._update_unsaved_changes_status()
        
        self.code_editor_view.clear_ai_content()
        self.main_window_view.show_info("AI Код", "Код добавлен в очередь изменений")
        self.main_window_view.set_status("AI код будет добавлен при сохранении проекта")

    def on_replace_selected_element(self):
        """Заменить выбранный элемент AI кодом."""
        selected_item = self.project_tree_view.get_selected_item()
        if not selected_item:
            self.main_window_view.show_warning("Замена", "Выберите элемент для замены")
            return
        
        ai_code = self.code_editor_view.get_ai_content()
        if not ai_code:
            self.main_window_view.show_warning("Замена", "Введите код для замены")
            return
        
        # Получаем старый код элемента
        old_code = ""
        if selected_item.get('path') and self.project_ast_tree:
            # Здесь нужно найти элемент в AST дереве и получить его код
            pass
        
        # Создаем отложенное изменение
        pending_change = PendingChange(
            action='replace',
            entity_name=selected_item.get('clean_name', selected_item.get('name')),
            new_code=ai_code,
            old_code=old_code,
            file_path=selected_item.get('path'),
            node_type=selected_item.get('type')
        )
        
        self.change_manager.add_change(pending_change)
        self._update_unsaved_changes_status()
        
        self.code_editor_view.clear_ai_content()
        self.main_window_view.show_info("Замена", "Элемент помещен в очередь замены")
        self.main_window_view.set_status("Элемент будет заменен при сохранении проекта")

    def on_clear_ai_code(self):
        """Очистить поле AI кода."""
        self.code_editor_view.clear_ai_content()
        self.main_window_view.set_status("Поле AI кода очищено")

    # --- Обработчики событий дерева ---
    
    def on_tree_item_selected_with_code_display(self):
        """Обработка выбора элемента дерева проекта с отображением кода элемента."""
        # Вызываем существующий обработчик
        self.on_tree_item_selected()
        
        # ДОПОЛНИТЕЛЬНО: Получаем и отображаем код элемента
        self._display_selected_element_code()
    
    def _display_selected_element_code(self):
        """Отображает код выбранного элемента в редакторе кода."""
        try:
            # Проверяем, есть ли метод получения кода элемента в ProjectTreeView
            if hasattr(self.project_tree_view, 'get_selected_element_code'):
                code = self.project_tree_view.get_selected_element_code()
                
                if code:
                    # Отображаем код элемента в редакторе исходного кода
                    self.code_editor_view.set_source_content(code)
                    
                    # Получаем информацию о выбранном элементе для статуса
                    selected_item = self.project_tree_view.get_selected_item()
                    if selected_item:
                        item_type = selected_item.get("type", "unknown")
                        item_name = selected_item.get("clean_name", selected_item.get("name", "unknown"))
                        
                        # Обновляем статус
                        if item_type == "file":
                            self.main_window_view.set_status(f"Показан файл: {item_name}")
                        elif item_type == "class":
                            self.main_window_view.set_status(f"Показан класс: {item_name}")
                        elif item_type in ["function", "async_function"]:
                            self.main_window_view.set_status(f"Показана функция: {item_name}")
                        elif item_type in ["method", "async_method"]:
                            self.main_window_view.set_status(f"Показан метод: {item_name}")
                        elif item_type == "import_section":
                            self.main_window_view.set_status(f"Показаны импорты")
                        elif item_type == "global_section":
                            self.main_window_view.set_status(f"Показан глобальный код")
                        else:
                            self.main_window_view.set_status(f"Показан элемент: {item_name}")
                    
                    # Сбрасываем флаг изменений для этого элемента
                    self.has_unsaved_changes = False
                    self.code_editor_view.update_modified_status(False)
                    self._update_unsaved_changes_status()
                    
                    logger.debug(f"Отображен код элемента: {len(code)} символов")
                else:
                    # Если код пустой, очищаем редактор
                    selected_item = self.project_tree_view.get_selected_item()
                    if selected_item:
                        item_type = selected_item.get("type", "unknown")
                        
                        # Для директорий и проектов показываем информационное сообщение
                        if item_type in ["directory", "project"]:
                            info_text = self._get_directory_info_text(selected_item)
                            self.code_editor_view.set_source_content(info_text)
                            
                            if item_type == "directory":
                                self.main_window_view.set_status(f"Показана директория: {selected_item.get('name', '')}")
                            else:
                                self.main_window_view.set_status(f"Показан проект: {selected_item.get('name', '')}")
                        else:
                            self.code_editor_view.set_source_content("")
            else:
                logger.warning("ProjectTreeView не поддерживает get_selected_element_code()")
                
        except Exception as e:
            logger.error(f"Ошибка при отображении кода элемента: {e}")
            self.main_window_view.show_error("Ошибка", f"Не удалось отобразить код элемента: {e}")
    
    def _get_directory_info_text(self, directory_item: dict) -> str:
        """Возвращает информационный текст для директории."""
        name = directory_item.get("name", "Директория")
        path = directory_item.get("path", "")
        
        info_lines = [
            f"# {name}",
            f"# Тип: {'Проект' if directory_item.get('type') == 'project' else 'Директория'}",
            f"# Путь: {path}",
            f"",
            f"# Содержимое:",
            f"# ------------",
            f""
        ]
        
        # Если это директория проекта, можно добавить статистику
        if directory_item.get('type') == 'project' and hasattr(self, 'project_service'):
            try:
                structure = self.project_service.get_project_structure()
                if structure:
                    files_count = len(structure.get('files', {}))
                    dirs_count = len(structure.get('directories', []))
                    modules_count = len(structure.get('modules', []))
                    
                    info_lines.extend([
                        f"# Статистика проекта:",
                        f"#   Файлов: {files_count}",
                        f"#   Директорий: {dirs_count}",
                        f"#   Модулей: {modules_count}",
                        f""
                    ])
            except Exception:
                pass
        
        info_lines.append("# Выберите конкретный файл или элемент кода для просмотра")
        
        return "\n".join(info_lines)
    
    def on_tree_item_selected(self):
        """Обработка выбора элемента дерева проекта (базовая логика)."""
        selected_item = self.project_tree_view.get_selected_item()
        if not selected_item:
            return
        
        item_type = selected_item.get("type")
        item_path = selected_item.get("path")
        item_name = selected_item.get("clean_name", selected_item.get("name"))
        
        # ОБНОВЛЕНИЕ: Убираем автоматическую загрузку файлов при выборе
        # Теперь файлы загружаются только при явном действии
        if item_type == "file":
            self.current_file_path = item_path
            
            # Обновляем статус, но не загружаем файл автоматически
            self.main_window_view.set_status(f"Выбран файл: {item_name}")
            
            # Если хотим сохранить возможность открывать файлы по двойному клику,
            # можно добавить отдельный обработчик
        elif item_type == "module":
            self.main_window_view.set_status(f"Выбран модуль: {item_name}")
        elif item_type == "directory":
            self.main_window_view.set_status(f"Выбрана директория: {item_name}")
        elif item_type == "class":
            self.main_window_view.set_status(f"Выбран класс: {item_name}")
        elif item_type in ["function", "async_function"]:
            self.main_window_view.set_status(f"Выбрана функция: {item_name}")
        elif item_type in ["method", "async_method"]:
            self.main_window_view.set_status(f"Выбран метод: {item_name}")
        elif item_type in ["import_section", "global_section"]:
            self.main_window_view.set_status(f"Выбрана секция кода")
            
    def on_open_selected_file(self):
        """Открыть выбранный файл (вместо показа кода элемента)."""
        selected_item = self.project_tree_view.get_selected_item()
        if not selected_item:
            self.main_window_view.show_warning("Открытие", "Выберите файл для открытия")
            return
        
        item_type = selected_item.get("type")
        item_path = selected_item.get("path")
        
        if item_type != "file":
            self.main_window_view.show_warning("Открытие", "Выберите файл, а не элемент кода")
            return
        
        # Проверяем несохраненные изменения
        if self.has_unsaved_changes and self.current_file_path:
            response = self.dialogs_view.ask_save_changes(os.path.basename(self.current_file_path))
            
            if response is None:  # Отмена
                return
            elif response:  # Сохранить
                self.on_save_current_file()
        
        # Загружаем файл
        self._load_file_content(item_path)

    def on_expand_all(self):
        """Раскрыть все ветки дерева."""
        self.project_tree_view.expand_all()

    def on_collapse_all(self):
        """Свернуть все ветки дерева."""
        self.project_tree_view.collapse_all()

    def on_find_next(self):
        """Следующий результат поиска."""
        self.project_tree_view.find_next()

    # --- Вспомогательные методы ---
    
    def _load_file_content(self, file_path: str):
        """Загружает содержимое файла в редактор."""
        try:
            content = self.project_service.repository.read_file(file_path)
            if content is not None:
                self.code_editor_view.set_source_content(content)
                self.current_file_path = file_path
                self.has_unsaved_changes = False
                self.code_editor_view.update_modified_status(False)
                self.project_service.repository.current_file_path = file_path
                self.main_window_view.set_status(f"Открыт файл: {os.path.basename(file_path)}")
                
                # Обновляем редактор AI-кода с анализом текущего файла
                self._update_ai_editor_with_analysis(file_path, content)
            else:
                self.main_window_view.show_error("Ошибка", f"Не удалось загрузить файл: {file_path}")
                
        except Exception as e:
            logger.error("Ошибка при загрузке файла %s: %s", file_path, e)
            self.main_window_view.show_error("Ошибка", f"Ошибка загрузки файла: {e}")

    def _update_ai_editor_with_analysis(self, file_path: str, content: str):
        """Обновляет редактор AI-кода с анализом текущего файла."""
        try:
            # Анализируем структуру файла для подсказок
            if self.project_ast_tree and file_path in self.project_ast_tree:
                module_node = self.project_ast_tree[file_path]
                
                # Создаем подсказку для AI-кода
                ai_hint = self._create_ai_hint_from_ast(module_node)
                
                # Если AI редактор пустой, добавляем подсказку
                current_ai_content = self.code_editor_view.get_ai_content()
                if not current_ai_content.strip():
                    self.code_editor_view.set_ai_content(ai_hint)
                    
        except Exception as e:
            logger.debug(f"Ошибка при обновлении AI редактора: {e}")

    def _create_ai_hint_from_ast(self, module_node) -> str:
        """Создает подсказку для AI-кода на основе AST."""
        hint_lines = ["# AI Код для автоматической интеграции\n"]
        hint_lines.append("# Введите код, который нужно добавить или заменить\n")
        hint_lines.append("# Примеры:\n")
        
        for child in module_node.children:
            if child.type == 'class':
                hint_lines.append(f"# class {child.name}: ...")
            elif child.type in ['function', 'async_function']:
                hint_lines.append(f"# def {child.name}(): ...")
        
        hint_lines.append("\n# Или введите структуру проекта:")
        hint_lines.append("# modules/")
        hint_lines.append("# ├── module1/")
        hint_lines.append("# │   ├── __init__.py")
        hint_lines.append("# │   └── file1.py")
        hint_lines.append("# └── main.py")
        
        return "\n".join(hint_lines)

    def _load_project_tree(self):
        """Перечитывает структуру проекта и отображает в дереве."""
        if not self.project_service or not self.project_service.project_path:
            self.main_window_view.show_warning("Проект", "Проект не открыт")
            return
        
        try:
            # Используем новый метод загрузки
            self.project_tree_view.load_from_project_service(self.project_service)
            
            # Сбрасываем состояние
            self.current_file_path = None
            self.has_unsaved_changes = False
            self.code_editor_view.set_source_content("")
            self.code_editor_view.clear_ai_content()
            self.code_editor_view.update_modified_status(False)
            self._update_unsaved_changes_status()
            self.main_window_view.set_status("Проект загружен")
            
            # Обновляем AST дерево для контроллера
            self._update_ast_tree(self.project_service.project_path)
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке проекта: {e}")
            self.main_window_view.show_error("Ошибка", f"Не удалось загрузить проект: {e}")

    def _clear_all_views(self):
        """Очищает все представления."""
        self.current_file_path = None
        self.has_unsaved_changes = False
        self.change_manager.clear_changes()
        self.project_ast_tree.clear()
        
        self.code_editor_view.set_source_content("")
        self.code_editor_view.clear_ai_content()
        self.code_editor_view.update_modified_status(False)
        self.analysis_view.clear_analysis()
        self.project_tree_view.tree.delete(*self.project_tree_view.tree.get_children())
        self.project_tree_view.search_var.set("")
        self.project_tree_view.search_results = []
        self.project_tree_view.current_search_index = -1
        
        self.main_window_view.set_unsaved_changes_status("")
        self.main_window_view.set_status("Проект не открыт")

    def _apply_pending_changes(self):
        """Применить отложенные изменения."""
        pending_changes = self.change_manager.get_pending_changes()
        if not pending_changes:
            logger.debug("Нет отложенных изменений для применения")
            return False
        
        try:
            # Конвертируем PendingChange в CodeChange
            from core.business.change_service import CodeChange
            code_changes = []
            for pending_change in pending_changes:
                code_change = CodeChange(
                    action=pending_change.action,
                    entity_name=pending_change.entity_name,
                    new_code=pending_change.new_code,
                    old_code=pending_change.old_code,
                    file_path=pending_change.file_path,
                    node_type=pending_change.node_type
                )
                code_changes.append(code_change)
            
            # Используем CodeManager для применения изменений
            success = self.code_manager.apply_changes(code_changes)
            
            if success:
                applied_count = len(pending_changes)
                self.change_manager.clear_changes()
                logger.info("Применено %s изменений", applied_count)
                
                # Обновляем дерево проекта
                self._load_project_tree()
                
                return True
            else:
                logger.error("Не удалось применить отложенные изменения")
                return False
                
        except Exception as e:
            logger.error("Ошибка применения отложенных изменений: %s", e)
            return False

    def _update_unsaved_changes_status(self):
        """Обновляет статус несохраненных изменений."""
        status_text = []
        
        # Проверяем отложенные изменения
        pending_changes = self.change_manager.get_pending_changes()
        if pending_changes:
            status_text.append(f"[{len(pending_changes)} отложенных]")
        
        # Проверяем несохраненные изменения в редакторе
        if self.has_unsaved_changes:
            status_text.append("[изменен]")
        
        self.main_window_view.set_unsaved_changes_status(" ".join(status_text))

    def get_project_info(self) -> Dict[str, Any]:
        """Возвращает информацию о текущем проекте."""
        return {
            'project_path': self.project_service.project_path,
            'project_name': self.project_service.project_name,
            'current_file': self.current_file_path,
            'has_unsaved_changes': self.has_unsaved_changes,
            'pending_changes_count': len(self.change_manager.get_pending_changes()),
            'auto_save_enabled': self.auto_save_on_blur,
            'ast_modules_count': len(self.project_ast_tree)
        }

    def analyze_code_quality(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Анализирует качество кода текущего файла или проекта
        
        Args:
            file_path: Путь к файлу для анализа (если None - весь проект)
            
        Returns:
            Dict с результатами анализа
        """
        try:
            if file_path:
                # Анализ одного файла
                content = self.code_service.get_file_content(file_path)
                ast_node = self.ast_service.parse_module(file_path)
                
                if ast_node:
                    return self._analyze_single_file(ast_node, content)
                else:
                    return {'error': 'Не удалось проанализировать файл'}
            else:
                # Анализ всего проекта
                if not self.project_ast_tree and self.project_service.project_path:
                    self.project_ast_tree = self.ast_service.parse_project(
                        self.project_service.project_path
                    )
                
                return self._analyze_project(self.project_ast_tree)
                
        except Exception as e:
            logger.error(f"Ошибка при анализе качества кода: {e}")
            return {'error': str(e)}

    def _analyze_single_file(self, ast_node, content: str) -> Dict[str, Any]:
        """Анализирует качество кода одного файла."""
        analysis = {
            'file_name': os.path.basename(self.current_file_path) if self.current_file_path else 'unknown',
            'total_lines': len(content.split('\n')),
            'classes_count': 0,
            'functions_count': 0,
            'methods_count': 0,
            'imports_count': 0,
            'issues': []
        }
        
        # Подсчитываем элементы
        for child in ast_node.children:
            if child.type == 'class':
                analysis['classes_count'] += 1
                analysis['methods_count'] += len(child.children)
            elif child.type in ['function', 'async_function']:
                analysis['functions_count'] += 1
            elif child.type == 'import_section':
                analysis['imports_count'] += 1
        
        # Проверяем на возможные проблемы
        if analysis['total_lines'] > 500:
            analysis['issues'].append('Файл слишком длинный (>500 строк)')
        
        if analysis['classes_count'] > 10:
            analysis['issues'].append('Слишком много классов в одном файле (>10)')
        
        return analysis

    def _analyze_project(self, project_tree: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует качество кода всего проекта."""
        analysis = {
            'files_count': len(project_tree),
            'total_classes': 0,
            'total_functions': 0,
            'total_methods': 0,
            'files_with_issues': []
        }
        
        for file_path, module_node in project_tree.items():
            file_analysis = self._analyze_single_file(module_node, module_node.source_code)
            
            analysis['total_classes'] += file_analysis['classes_count']
            analysis['total_functions'] += file_analysis['functions_count']
            analysis['total_methods'] += file_analysis['methods_count']
            
            if file_analysis['issues']:
                analysis['files_with_issues'].append({
                    'file': os.path.basename(file_path),
                    'issues': file_analysis['issues']
                })
        
        return analysis

    def generate_code_summary(self) -> str:
        """Генерирует краткую сводку по коду проекта."""
        project_info = self.get_project_info()
        
        summary_lines = [
            f"=== Сводка проекта ===",
            f"Проект: {project_info.get('project_name', 'Не открыт')}",
            f"Путь: {project_info.get('project_path', 'Н/Д')}",
            f"Текущий файл: {project_info.get('current_file', 'Нет')}",
            f"Несохраненные изменения: {'Да' if project_info['has_unsaved_changes'] else 'Нет'}",
            f"Отложенные изменения: {project_info['pending_changes_count']}",
            f"Автосохранение: {'Включено' if project_info['auto_save_enabled'] else 'Выключено'}",
            f"AST модулей: {project_info['ast_modules_count']}"
        ]
        
        if project_info.get('project_path'):
            analysis = self.analyze_code_quality()
            summary_lines.extend([
                f"\n=== Анализ кода ===",
                f"Файлов: {analysis.get('files_count', 0)}",
                f"Классов: {analysis.get('total_classes', 0)}",
                f"Функций: {analysis.get('total_functions', 0)}",
                f"Методов: {analysis.get('total_methods', 0)}",
                f"Файлов с проблемами: {len(analysis.get('files_with_issues', []))}"
            ])
        
        return "\n".join(summary_lines)

    def export_project_analysis(self, export_path: Optional[str] = None):
        """Экспортирует анализ проекта в файл."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Экспорт", "Нет открытого проекта")
            return
        
        try:
            if not export_path:
                # Предлагаем выбрать путь для сохранения
                import tkinter.filedialog as fd
                export_path = fd.asksaveasfilename(
                    title="Экспорт анализа проекта",
                    defaultextension=".txt",
                    filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
                )
            
            if export_path:
                summary = self.generate_code_summary()
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
                self.main_window_view.show_info("Экспорт", f"Анализ экспортирован в: {export_path}")
                self.main_window_view.set_status(f"Анализ экспортирован: {os.path.basename(export_path)}")
                
        except Exception as e:
            logger.error(f"Ошибка при экспорте анализа: {e}")
            self.main_window_view.show_error("Экспорт", f"Ошибка: {e}")

    def show_help(self):
        """Показать справку по использованию приложения."""
        help_text = """
        === AI Code Assistant - Справка ===
        
        Основные функции:
        
        1. Управление проектом:
           - Создание нового проекта (🆕)
           - Открытие существующего проекта (📁)
           - Сохранение проекта (💾)
           - Закрытие проекта (❌)
        
        2. Работа с кодом:
           - Редактирование исходного кода (верхний редактор)
           - Ввод AI-кода/сценариев (нижний редактор)
           - Добавление AI-кода в проект (➕)
           - Замена кода AI-кодом (🔄)
           - Удаление элементов (🗑️)
        
        3. Анализ кода:
           - Статический анализ проекта (🔍)
           - Просмотр отчета анализа (📊)
           - Автоматический рефакторинг (🛠️)
        
        4. Дополнительные возможности:
           - Показать AST структуру (📊) - кнопка в дереве
           - Найти конфликты кода (🔍) - кнопка в дереве
           - Сгенерировать документацию (📝) - кнопка в дереве
           - Сравнить версии (🔄) - кнопка в дереве
        
        5. Дерево проекта:
           - Быстрый поиск элементов
           - Раскрыть все ветки (👁️)
           - Свернуть все ветки (🙈)
           - Следующий результат поиска (🔍)
        
        Горячие клавиши:
        - Ctrl+S: Сохранить текущий файл
        - Ctrl+O: Открыть проект
        - Ctrl+N: Создать новый проект
        - Ctrl+F: Поиск в дереве проекта
        
        Подсказки:
        - Наведите курсор на любую кнопку для получения подсказки
        - Используйте автосохранение для автоматического сохранения при переключении между файлами
        - AI-код автоматически анализируется на конфликты перед добавлением
        
        Для получения дополнительной помощи посетите документацию.
        """
        
        self.dialogs_view.show_info_dialog("Справка", help_text)