# gui/controller/main_controller.py

import os
import logging
from typing import Optional

from gui.views.main_window_view import IMainWindowView
from gui.views.code_editor_view import ICodeEditorView
from gui.views.project_tree_view import IProjectTreeView
from gui.views.dialogs_view import DialogsView
from core.business.project_service import IProjectService
from core.business.code_service import ICodeService
from core.business.analysis_service import IAnalysisService
from core.models.code_model import CodeNode

logger = logging.getLogger('ai_code_assistant')


class MainController:
    """
    Основной контроллер, интегрирующий функционал отложенных изменений
    и управление проектами из старого кода.
    """
    
    def __init__(
        self,
        main_window_view: IMainWindowView,
        code_editor_view: ICodeEditorView,
        project_tree_view: IProjectTreeView,
        dialogs_view: DialogsView,
        project_service: IProjectService,
        code_service: ICodeService,
        analysis_service: IAnalysisService,
    ):
        self.main_window_view = main_window_view
        self.code_editor_view = code_editor_view
        self.project_tree_view = project_tree_view
        self.dialogs_view = dialogs_view
        self.project_service = project_service
        self.code_service = code_service
        self.analysis_service = analysis_service
        
        # Состояние контроллера
        self.current_file_path: Optional[str] = None
        self.has_unsaved_changes = False
        self.auto_save_on_blur = False
        
        # Инициализация отложенных изменений (упрощенная версия)
        self.pending_changes = []
        
        # Привязка GUI-событий
        self._setup_event_bindings()
        
        logger.info("MainController инициализирован")

    def _setup_event_bindings(self):
        """Настраивает привязки событий GUI"""
        self.main_window_view.bind_create_project(self.on_create_project_clicked)
        self.main_window_view.bind_open_project(self.on_open_project_clicked)
        self.main_window_view.bind_create_structure(self.on_create_project_structure_from_ai)
        
        self.code_editor_view.bind_on_text_modified(self.on_code_modified)
        self.code_editor_view.bind_focus_out(self.on_editor_focus_out)
        
        self.project_tree_view.set_on_tree_select_callback(self.on_tree_item_selected)
        
        logger.debug("Привязки событий настроены")

    # --- Обработчики событий проекта ---
    
    def on_create_project_clicked(self):
        """Обработка создания нового проекта."""
        result = self.dialogs_view.show_project_creation_dialog(self.project_service)
        
        if result:
            path, name, template_name, is_empty, full_path = result
            success = self.project_service.create_project(path, name)
            
            if success:
                self.main_window_view.set_status(f"Проект создан: {name}")
                self.main_window_view.show_info("Успех", "Проект успешно создан!")
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
                self._load_project_tree()
            else:
                self.main_window_view.show_error("Ошибка", "Не удалось открыть проект!")

    def on_create_project_structure_from_ai(self):
        """Генерация структуры проекта по AI-схеме."""
        schema = self.code_editor_view.get_ai_content()
        if not schema:
            self.main_window_view.show_warning("AI Схема", "Введите AI-схему!")
            return
        
        success = self.project_service.create_structure_from_ai(schema)
        if success:
            self.main_window_view.show_info("Структура проекта", "Генерация структуры завершена!")
            self._load_project_tree()
        else:
            self.main_window_view.show_error("Ошибка", "Ошибка генерации структуры из AI-схемы.")

    # --- Обработчики событий редактора ---
    
    def on_code_modified(self, event=None):
        """Автосохранение при изменении кода."""
        if not self.current_file_path:
            return
        
        content = self.code_editor_view.get_source_content()
        success = self.code_service.save_current_file(content)
        
        if success:
            self.has_unsaved_changes = False
            self.code_editor_view.update_modified_status(False)
            self.main_window_view.set_status("Изменения сохранены")
        else:
            self.has_unsaved_changes = True
            self.code_editor_view.update_modified_status(True)
            self.main_window_view.set_status("Ошибка сохранения")

    def on_editor_focus_out(self, event=None):
        """Обработчик потери фокуса редактором (автосохранение)."""
        if self.auto_save_on_blur and self.has_unsaved_changes and self.current_file_path:
            logger.info("Автосохранение при потере фокуса для файла: %s", self.current_file_path)
            self.on_code_modified()

    # --- Обработчики событий дерева проекта ---
    
    def on_tree_item_selected(self):
        """Обработка выбора элемента дерева проекта."""
        selected_item = self.project_tree_view.get_selected_item()
        if not selected_item:
            return
        
        item_type = selected_item.get("type")
        item_path = selected_item.get("path")
        
        if item_type == "file":
            self._load_file_content(item_path)
        elif item_type == "module":
            self.main_window_view.set_status(f"Выбран модуль: {item_path}")

    def _load_file_content(self, file_path: str):
        """Загружает содержимое файла в редактор."""
        try:
            # Проверяем несохраненные изменения
            if self.has_unsaved_changes and self.current_file_path:
                result = self.dialogs_view.ask_save_changes(os.path.basename(self.current_file_path))
                
                if result is None:  # Отмена
                    return
                elif result:  # Сохранить
                    self.on_code_modified()
            
            # Загружаем новый файл
            content = self.project_service.repository.read_file(file_path)
            if content is not None:
                self.code_editor_view.set_source_content(content)
                self.current_file_path = file_path
                self.has_unsaved_changes = False
                self.project_service.repository.current_file_path = file_path
                self.main_window_view.set_status(f"Открыт файл: {file_path}")
            else:
                self.main_window_view.show_error("Ошибка", f"Не удалось загрузить файл: {file_path}")
                
        except Exception as e:
            logger.error("Ошибка при загрузке файла %s: %s", file_path, e)
            self.main_window_view.show_error("Ошибка", f"Ошибка загрузки файла: {e}")

    # --- Вспомогательные методы ---
    
    def _load_project_tree(self):
        """Перечитывает структуру проекта и отображает в дереве."""
        structure = self.project_service.repository.get_project_structure()
        self.project_tree_view.fill_tree(structure)
        
        # Сбрасываем состояние
        self.current_file_path = None
        self.has_unsaved_changes = False
        self.code_editor_view.set_source_content("")
        self.code_editor_view.clear_ai_content()

    # --- Методы для работы с отложенными изменениями ---
    
    def add_pending_change(self, change):
        """Добавляет отложенное изменение."""
        self.pending_changes.append(change)
        self._update_unsaved_changes_status()

    def apply_pending_changes(self):
        """Применяет все отложенные изменения."""
        # Базовая реализация - в реальном приложении нужно обрабатывать каждый change
        if self.pending_changes:
            success_count = 0
            for change in self.pending_changes:
                # Здесь должна быть логика применения конкретного изменения
                success_count += 1
            
            self.pending_changes = []
            self._update_unsaved_changes_status()
            return success_count > 0
        return False

    def _update_unsaved_changes_status(self):
        """Обновляет статус несохраненных изменений."""
        has_changes = len(self.pending_changes) > 0 or self.has_unsaved_changes
        # Можно добавить отображение статуса в MainWindowView
        if has_changes:
            logger.debug("Есть несохраненные изменения: pending=%s, editor=%s", 
                        len(self.pending_changes), self.has_unsaved_changes)

    # --- Методы интеграции анализа кода ---
    
    def on_analyze_code(self):
        """Запустить анализ проекта."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Анализ", "Сначала откройте проект")
            return
        
        success = self.analysis_service.analyze_code(self.project_service.project_path)
        if success:
            self.main_window_view.show_info("Анализ", "Анализ проекта завершён!")
        else:
            self.main_window_view.show_error("Анализ", "Ошибка анализа кода.")

    def on_show_analysis_report(self):
        """Показать отчёт анализа."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Анализ", "Сначала откройте проект")
            return
        
        report = self.analysis_service.get_report(self.project_service.project_path)
        if report:
            self.dialogs_view.show_info_dialog("Отчёт анализа", report)
        else:
            self.dialogs_view.show_warning("Отчёт анализа", "Нет результатов анализа.")

    def on_auto_refactor(self):
        """Запустить автоматический рефакторинг."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Рефакторинг", "Сначала откройте проект")
            return
        
        success = self.analysis_service.auto_refactor(self.project_service.project_path)
        if success:
            self.main_window_view.show_info("Рефакторинг", "Автоматический рефакторинг завершён!")
        else:
            self.main_window_view.show_error("Рефакторинг", "Ошибка рефакторинга.")

    # --- Методы управления автосохранением ---
    
    def set_auto_save_on_blur(self, enabled: bool):
        """Включает/выключает автосохранение при потере фокуса."""
        self.auto_save_on_blur = enabled
        logger.info("Автосохранение при потере фокуса: %s", "включено" if enabled else "выключено")

    def get_project_info(self):
        """Возвращает информацию о текущем проекте."""
        return {
            'has_unsaved_changes': self.has_unsaved_changes,
            'pending_changes_count': len(self.pending_changes),
            'current_file': self.current_file_path,
            'auto_save_enabled': self.auto_save_on_blur
        }