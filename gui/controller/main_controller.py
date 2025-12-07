# gui/controller/main_controller.py

import os
import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

from gui.views.main_window_view import IMainWindowView
from gui.views.code_editor_view import ICodeEditorView
from gui.views.project_tree_view import IProjectTreeView
from gui.views.dialogs_view import DialogsView
from gui.views.analysis_view import IAnalysisView
from core.business.project_service import IProjectService
from core.business.code_service import ICodeService
from core.business.analysis_service import IAnalysisService

logger = logging.getLogger('ai_code_assistant')


class MainController:
    """
    Основной контроллер с точной структурой размещения как в старом коде.
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
        
        # Состояние контроллера
        self.current_file_path: Optional[str] = None
        self.has_unsaved_changes = False
        self.auto_save_on_blur = False
        self.pending_changes = []
        
        # Инициализация GUI с точной структурой
        self._setup_gui_structure()
        self._setup_event_bindings()
        
        logger.info("MainController инициализирован с точной структурой GUI")

    def _setup_gui_structure(self):
        """Настраивает точную структуру GUI как в старом коде."""
        # Получаем панель контента из MainWindowView
        content_panel = self.main_window_view.get_content_panel()
        
        # Создаем главную область контента
        content_frame = ttk.Frame(content_panel)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - дерево проекта (фиксированная ширина 300px)
        left_panel = ttk.Frame(content_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False)  # Фиксируем ширину
        
        # Настраиваем компоненты в левой панели
        self.project_tree_view.setup_search_panel(left_panel)
        self.project_tree_view.setup_tree_buttons(left_panel)
        self.project_tree_view.setup_tree()
        self.project_tree_view.pack(in_=left_panel, fill=tk.BOTH, expand=True)
        
        # Правая панель - редакторы кода и анализ
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Верхняя часть правой панели - редакторы кода
        editor_container = ttk.Frame(right_panel)
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Размещаем CodeEditorView
        self.code_editor_view.pack(in_=editor_container, fill=tk.BOTH, expand=True)
        
        # Нижняя часть правой панели - анализ кода (фиксированная высота)
        analysis_container = ttk.Frame(right_panel, height=200)
        analysis_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        analysis_container.pack_propagate(False)  # Фиксируем высоту
        
        # Размещаем AnalysisView
        self.analysis_view.pack(in_=analysis_container, fill=tk.BOTH, expand=True)
        self.analysis_view.setup_analysis_panel(analysis_container)
        
        logger.debug("GUI структура настроена как в старом коде")

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
        self.project_tree_view.expand_all_button.config(command=self.on_expand_all)
        self.project_tree_view.collapse_all_button.config(command=self.on_collapse_all)
        self.project_tree_view.find_next_button.config(command=self.on_find_next)
        
        # Редактор
        self.code_editor_view.bind_on_text_modified(self.on_code_modified)
        self.code_editor_view.bind_focus_out(self.on_editor_focus_out)
        
        # Дерево проекта
        self.project_tree_view.set_on_tree_select_callback(self.on_tree_item_selected)
        
        # Анализ
        self.analysis_view.bind_analyze_code(self.on_analyze_code)
        self.analysis_view.bind_show_analysis_report(self.on_show_analysis_report)
        self.analysis_view.bind_auto_refactor(self.on_auto_refactor)
        
        # Настройка автосохранения (создаем переменную как в старом коде)
        self.auto_save_var = tk.BooleanVar(value=False)
        self.code_editor_view.setup_auto_save_checkbox(self.auto_save_var)
        self.auto_save_var.trace_add('write', self._on_auto_save_changed)
        
        logger.debug("Привязки событий настроены")

    def _on_auto_save_changed(self, *args):
        """Обработчик изменения состояния автосохранения."""
        self.auto_save_on_blur = self.auto_save_var.get()
        logger.info("Автосохранение: %s", "включено" if self.auto_save_on_blur else "выключено")

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

    def on_refresh_project(self):
        """Обновить проект."""
        if self.project_service.project_path:
            self._load_project_tree()
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
        
        # Применить отложенные изменения
        if self.pending_changes:
            self.apply_pending_changes()
        
        self.main_window_view.show_info("Сохранение", "Проект сохранен")
        self.main_window_view.set_status("Проект сохранен")

    def on_show_pending_changes(self):
        """Показать отложенные изменения."""
        if not self.pending_changes:
            self.main_window_view.show_info("Отложенные изменения", "Нет отложенных изменений")
            return
        
        # Показываем диалог с отложенными изменениями
        apply_changes = self.dialogs_view.show_pending_changes_dialog(self.pending_changes)
        
        if apply_changes:
            self.apply_pending_changes()
            self.main_window_view.show_info("Изменения", "Отложенные изменения применены")
        else:
            self.pending_changes = []
            self._update_unsaved_changes_status()
            self.main_window_view.show_info("Изменения", "Отложенные изменения отменены")

    def on_close_project(self):
        """Закрыть проект."""
        if not self.project_service.project_path:
            self.main_window_view.show_warning("Закрытие", "Нет открытого проекта")
            return
        
        # Проверяем несохраненные изменения
        if self.has_unsaved_changes or self.pending_changes:
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
        
        # Пример анализа
        self.analysis_view.add_analysis_result("info", "Начало анализа проекта")
        
        try:
            # Используем сервис анализа
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
            # Добавляем в отложенные изменения
            self.pending_changes.append({
                'action': 'delete',
                'entity': selected_item.get('clean_name', selected_item.get('name')),
                'file': selected_item.get('path'),
                'type': selected_item.get('type')
            })
            
            self._update_unsaved_changes_status()
            self.main_window_view.show_info("Удаление", "Элемент помечен для удаления")
            self.main_window_view.set_status(f"Элемент будет удален при сохранении")

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
        
        # Добавляем в отложенные изменения
        self.pending_changes.append({
            'action': 'add',
            'entity': 'AI код',
            'file': selected_item.get('path'),
            'type': 'ai_code',
            'code': ai_code
        })
        
        self._update_unsaved_changes_status()
        self.code_editor_view.clear_ai_content()
        self.main_window_view.show_info("AI Код", "Код добавлен в очередь изменений")
        self.main_window_view.set_status("AI код будет добавлен при сохранении")

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
        
        # Добавляем в отложенные изменения
        self.pending_changes.append({
            'action': 'replace',
            'entity': selected_item.get('clean_name', selected_item.get('name')),
            'file': selected_item.get('path'),
            'type': selected_item.get('type'),
            'code': ai_code
        })
        
        self._update_unsaved_changes_status()
        self.code_editor_view.clear_ai_content()
        self.main_window_view.show_info("Замена", "Элемент помечен для замены")
        self.main_window_view.set_status(f"Элемент будет заменен при сохранении")

    def on_clear_ai_code(self):
        """Очистить поле AI кода."""
        self.code_editor_view.clear_ai_content()
        self.main_window_view.set_status("Поле AI кода очищено")

    # --- Обработчики событий дерева ---
    
    def on_tree_item_selected(self):
        """Обработка выбора элемента дерева проекта."""
        selected_item = self.project_tree_view.get_selected_item()
        if not selected_item:
            return
        
        item_type = selected_item.get("type")
        item_path = selected_item.get("path")
        item_name = selected_item.get("clean_name", selected_item.get("name"))
        
        if item_type == "file":
            # Проверяем несохраненные изменения
            if self.has_unsaved_changes and self.current_file_path:
                response = self.dialogs_view.ask_save_changes(os.path.basename(self.current_file_path))
                
                if response is None:  # Отмена
                    return
                elif response:  # Сохранить
                    self.on_save_current_file()
            
            # Загружаем файл
            self._load_file_content(item_path)
        elif item_type == "module":
            self.main_window_view.set_status(f"Выбран модуль: {item_name}")
        elif item_type == "directory":
            self.main_window_view.set_status(f"Выбрана директория: {item_name}")

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
            else:
                self.main_window_view.show_error("Ошибка", f"Не удалось загрузить файл: {file_path}")
                
        except Exception as e:
            logger.error("Ошибка при загрузке файла %s: %s", file_path, e)
            self.main_window_view.show_error("Ошибка", f"Ошибка загрузки файла: {e}")

    def _load_project_tree(self):
        """Перечитывает структуру проекта и отображает в дереве."""
        structure = self.project_service.repository.get_project_structure()
        self.project_tree_view.fill_tree(structure)
        
        # Сбрасываем состояние
        self.current_file_path = None
        self.has_unsaved_changes = False
        self.code_editor_view.set_source_content("")
        self.code_editor_view.clear_ai_content()
        self.code_editor_view.update_modified_status(False)
        self._update_unsaved_changes_status()
        self.main_window_view.set_status("Проект загружен")

    def _clear_all_views(self):
        """Очищает все представления."""
        self.current_file_path = None
        self.has_unsaved_changes = False
        self.pending_changes = []
        
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

    def apply_pending_changes(self):
        """Применить отложенные изменения."""
        if not self.pending_changes:
            return False
        
        try:
            # Применяем изменения через сервис
            success_count = 0
            for change in self.pending_changes:
                try:
                    if change['action'] == 'add':
                        if self.code_service.add_code(
                            change['file'],
                            change['code'],
                            change.get('position', 'end')
                        ):
                            success_count += 1
                    
                    elif change['action'] == 'replace':
                        if self.code_service.replace_code(
                            change['file'],
                            change['entity'],
                            change['code']
                        ):
                            success_count += 1
                    
                    elif change['action'] == 'delete':
                        if self.code_service.delete_code(
                            change['file'],
                            change['entity']
                        ):
                            success_count += 1
                            
                except Exception as e:
                    logger.error("Ошибка применения изменения: %s", e)
            
            # Очищаем список изменений
            self.pending_changes = []
            self._update_unsaved_changes_status()
            
            # Обновляем дерево проекта
            self._load_project_tree()
            
            logger.info("Применено %s изменений", success_count)
            return True
            
        except Exception as e:
            logger.error("Ошибка применения отложенных изменений: %s", e)
            return False

    def _update_unsaved_changes_status(self):
        """Обновляет статус несохраненных изменений."""
        status_text = []
        if self.pending_changes:
            status_text.append(f"[{len(self.pending_changes)} отложенных]")
        if self.has_unsaved_changes:
            status_text.append("[изменен]")
        
        self.main_window_view.set_unsaved_changes_status(" ".join(status_text))

    def get_project_info(self):
        """Возвращает информацию о текущем проекте."""
        return {
            'has_unsaved_changes': self.has_unsaved_changes,
            'pending_changes_count': len(self.pending_changes),
            'current_file': self.current_file_path,
            'auto_save_enabled': self.auto_save_on_blur
        }