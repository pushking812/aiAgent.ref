# gui/controller/analysis_controller.py

from gui.views.main_window_view import IMainWindowView
from gui.views.dialogs_view import DialogsView
from core.business.analysis_service import IAnalysisService

class AnalysisController:
    """
    Контроллер для управления функциями анализа кода и рефакторинга.
    """
    def __init__(
        self,
        main_window_view: IMainWindowView,
        dialogs_view: DialogsView,
        analysis_service: IAnalysisService,
    ):
        self.main_window_view = main_window_view
        self.dialogs_view = dialogs_view
        self.analysis_service = analysis_service

    def on_analyze_code(self, project_path):
        """
        Запустить анализ кода всего проекта.
        """
        success = self.analysis_service.analyze_code(project_path)
        if success:
            self.main_window_view.show_info("Анализ", "Анализ кода завершён успешно.")
        else:
            self.main_window_view.show_error("Анализ", "Ошибка выполнения анализа.")

    def on_show_analysis_report(self, project_path):
        """
        Отобразить отчёт анализа кода (например, рекомендации, ошибки).
        """
        report = self.analysis_service.get_report(project_path)
        if report:
            self.dialogs_view.show_info_dialog("Отчёт анализа", report)
        else:
            self.dialogs_view.show_warning("Отчёт анализа", "Отчёт отсутствует или пуст.")

    def on_auto_refactor(self, project_path):
        """
        Запустить автоматический рефакторинг кода проекта.
        """
        success = self.analysis_service.auto_refactor(project_path)
        if success:
            self.main_window_view.show_info("Рефакторинг", "Автоматический рефакторинг завершён успешно.")
        else:
            self.main_window_view.show_error("Рефакторинг", "Ошибка рефакторинга кода.")

    def on_show_diff(self, old_code, new_code):
        """
        Показать различия между двумя версиями кода.
        """
        import difflib
        diff = "\n".join(difflib.unified_diff(
            old_code.splitlines(), new_code.splitlines(),
            fromfile="Старый", tofile="Новый"))
        self.dialogs_view.show_diff(diff, title="Сравнение изменений анализа")