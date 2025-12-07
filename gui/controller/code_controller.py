# gui/controller/code_controller.py

from gui.views.code_editor_view import ICodeEditorView
from gui.views.main_window_view import IMainWindowView
from gui.views.dialogs_view import DialogsView
from core.business.code_service import ICodeService
import difflib

class CodeController:
    """
    Контроллер для управления функциями редактора кода и работы с AI-кодом.
    """
    def __init__(
        self,
        code_view: ICodeEditorView,
        main_window_view: IMainWindowView,
        dialogs_view: DialogsView,
        code_service: ICodeService,
    ):
        self.code_view = code_view
        self.main_window_view = main_window_view
        self.dialogs_view = dialogs_view
        self.code_service = code_service

        # Привязка событий редактора
        self.code_view.bind_on_text_modified(self.on_text_modified)
        self.code_view.bind_on_ai_modified(self.on_ai_modified)

    def on_text_modified(self, event=None):
        """
        Обработка изменения текстового поля исходного кода.
        Обычно авто-сохранение или индикатор несохранённых изменений.
        """
        content = self.code_view.get_source_content()
        success = self.code_service.save_current_file(content)
        if success:
            self.main_window_view.set_status("Изменения сохранены")
        else:
            self.main_window_view.set_status("Ошибка сохранения")

    def on_ai_modified(self, event=None):
        """
        Можно реализовать автосинхронизацию AI-поля, генерацию/валидатор.
        """
        ai_code = self.code_view.get_ai_content()
        # Здесь можно анализировать или валидировать AI-код
        if ai_code:
            self.main_window_view.set_status(f"AI-код: {len(ai_code)} символов")

    def on_add_ai_code(self):
        """
        Добавить AI-код к текущему файлу.
        """
        ai_code = self.code_view.get_ai_content()
        if not ai_code:
            self.main_window_view.show_warning("AI-код", "Поле AI-кода пустое")
            return
        success = self.code_service.add_ai_code(ai_code)
        if success:
            self.main_window_view.show_info("AI-код", "AI-код успешно добавлен!")
            self.code_view.clear_ai_content()
        else:
            self.main_window_view.show_error("AI-код", "Ошибка при добавлении AI-кода!")

    def on_replace_code(self, file_path, node_name):
        """
        Заменить выбранный элемент кода новым AI-кодом.
        """
        ai_code = self.code_view.get_ai_content()
        if not ai_code:
            self.main_window_view.show_warning("Замена кода", "Введите новый код для замены!")
            return
        success = self.code_service.replace_code(file_path, node_name, ai_code)
        if success:
            self.main_window_view.show_info("Замена кода", "Элемент успешно заменён!")
            self.code_view.clear_ai_content()
        else:
            self.main_window_view.show_error("Замена кода", "Ошибка замены кода!")

    def on_clear_ai_code(self):
        """
        Очистить поле AI-кода.
        """
        self.code_view.clear_ai_content()
        self.main_window_view.set_status("Поле AI-кода очищено")

    def on_show_file_diff(self, old_code, new_code):
        """
        Показать различия между версиями файла (diff).
        """
        diff = "\n".join(
            difflib.unified_diff(
                old_code.splitlines(), new_code.splitlines(), 
                fromfile="Старый", tofile="Новый", lineterm=""
            )
        )
        if diff:
            self.dialogs_view.show_diff(diff, title="Сравнение версий файла")
        else:
            self.main_window_view.show_info("Сравнение", "Файлы идентичны")