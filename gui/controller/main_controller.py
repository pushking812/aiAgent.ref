# gui/controller/main_controller.py

from gui.views.main_window_view import IMainWindowView
from gui.views.code_editor_view import ICodeEditorView
from gui.views.project_tree_view import IProjectTreeView
from gui.views.dialogs_view import DialogsView
from core.business.project_service import IProjectService
from core.business.code_service import ICodeService
from core.business.analysis_service import IAnalysisService

class MainController:
    """
    Организует взаимодействие между главными View-компонентами и сервисами.
    Реализует бизнес-потоки: работа с проектом, кодом, анализ, обработку событий.
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

        # Привязка GUI-событий к методам контроллера
        self.main_window_view.bind_create_project(self.on_create_project_clicked)
        self.main_window_view.bind_open_project(self.on_open_project_clicked)
        self.main_window_view.bind_create_structure(self.on_create_project_structure_from_ai)
        self.code_editor_view.bind_on_text_modified(self.on_code_modified)
        self.project_tree_view.bind_on_select(self.on_tree_item_selected)

    # --- Методы обработки событий GUI ---

    def on_create_project_clicked(self):
        """
        Обработка создания нового проекта.
        Можно расширить диалогом выбора пути/имени.
        """
        # В реальной реализации получить имя/путь проекта через диалог
        path = "work_dir"      # Пример значения
        name = "NewProject"    # Пример значения
        success = self.project_service.create_project(path, name)
        if success:
            self.main_window_view.set_status(f"Проект: {name}")
            self.main_window_view.show_info("Успех", "Проект успешно создан!")
            self.load_project_tree()
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось создать проект!")

    def on_open_project_clicked(self):
        """
        Обработка открытия существующего проекта.
        """
        # Обычно путь выбирает пользователь — здесь заглушка
        path = "work_dir/Project1"
        success = self.project_service.open_project(path)
        if success:
            self.main_window_view.set_status(f"Открыт проект: {path}")
            self.load_project_tree()
        else:
            self.main_window_view.show_error("Ошибка", "Не удалось открыть проект!")

    def on_create_project_structure_from_ai(self):
        """
        Генерация структуры проекта по введённой AI-схеме/описанию.
        """
        schema = self.code_editor_view.get_ai_content()
        if not schema:
            self.main_window_view.show_warning("AI Схема", "Введите AI-схему!")
            return
        success = self.project_service.create_structure_from_ai(schema)
        if success:
            self.main_window_view.show_info("Структура проекта", "Генерация структуры завершена!")
            self.load_project_tree()
        else:
            self.main_window_view.show_error("Ошибка", "Ошибка генерации структуры из AI-схемы.")

    def on_code_modified(self, event=None):
        """
        Автосохранение при изменении кода (можно расширить).
        """
        content = self.code_editor_view.get_source_content()
        success = self.code_service.save_current_file(content)
        self.main_window_view.set_status("Изменения сохранены" if success else "Ошибка сохранения")

    def on_tree_item_selected(self, event=None):
        """
        Обработка выбора элемента дерева проекта (файл, модуль).
        Загружает содержимое файла в редактор, если выбран файл.
        """
        item = self.project_tree_view.get_selected_item()
        if item.get("type") == "file":
            file_path = item.get("name")
            content = self.project_service.repository.read_file(file_path)
            self.code_editor_view.set_source_content(content)
            self.project_service.repository.current_file_path = file_path
            self.main_window_view.set_status(f"Открыт файл: {file_path}")

    # --- Вспомогательные методы ---
    def load_project_tree(self):
        """
        Перечитать структуру проекта и отобразить в дереве.
        """
        structure = self.project_service.repository.get_project_structure()
        self.project_tree_view.fill_tree(structure)

    # --- Методы для диалогов, сравнения и т.д. ---
    def on_save_request(self, filename):
        """
        Показывает диалог сохранения. Пример использования DialogsView.
        """
        result = self.dialogs_view.ask_save_changes(filename)
        if result is True:
            content = self.code_editor_view.get_source_content()
            self.code_service.save_current_file(content)
        elif result is False:
            pass # Не сохранять
        else:
            pass # Отмена действия

    def on_show_diff(self, old_text, new_text):
        """
        Показывает окно сравнения двух текстов (Diff).
        """
        # Простое отображение разницы текстов
        import difflib
        diff = "\n".join(difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), fromfile='Старый', tofile='Новый'))
        self.dialogs_view.show_diff(diff, title="Сравнение изменений")

    # --- Методы интеграции анализа кода ---
    def on_analyze_code(self):
        """
        Запустить анализ проекта.
        """
        project_path = self.project_service.project_path
        success = self.analysis_service.analyze_code(project_path)
        if success:
            self.main_window_view.show_info("Анализ", "Анализ проекта завершён!")
        else:
            self.main_window_view.show_error("Анализ", "Ошибка анализа кода.")

    def on_show_analysis_report(self):
        """
        Показать отчёт анализа.
        """
        project_path = self.project_service.project_path
        report = self.analysis_service.get_report(project_path)
        if report:
            self.dialogs_view.show_info_dialog("Отчёт анализа", report)
        else:
            self.dialogs_view.show_info_dialog("Отчёт анализа", "Нет результатов анализа.")

    def on_auto_refactor(self):
        """
        Запустить автоматический рефакторинг.
        """
        project_path = self.project_service.project_path
        success = self.analysis_service.auto_refactor(project_path)
        if success:
            self.main_window_view.show_info("Рефакторинг", "Автоматический рефакторинг завершён!")
        else:
            self.main_window_view.show_error("Рефакторинг", "Ошибка рефакторинга.")