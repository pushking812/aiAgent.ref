# core/business/analysis_service.py

from abc import ABC, abstractmethod

class IAnalysisService(ABC):
    def analyze_code(self, project_path: str) -> bool: pass
    def get_report(self, project_path: str) -> str: pass
    def auto_refactor(self, project_path: str) -> bool: pass

class AnalysisService(IAnalysisService):
    """
    Сервис аналитики и рефакторинга кода; работает через связанный анализатор.
    """
    def __init__(self, analyzer):
        self.analyzer = analyzer  # Класс или объект-анализатор (например, AST/статический анализатор)

    def analyze_code(self, project_path: str) -> bool:
        """
        Запуск анализа кода в проекте.
        """
        try:
            return self.analyzer.run_analysis(project_path)
        except Exception as e:
            print(f"Ошибка анализа кода: {e}")
            return False

    def get_report(self, project_path: str) -> str:
        """
        Получение последнего отчёта анализа для проекта.
        """
        try:
            return self.analyzer.get_latest_report(project_path)
        except Exception as e:
            print(f"Ошибка получения отчёта анализа: {e}")
            return ""

    def auto_refactor(self, project_path: str) -> bool:
        """
        Запуск автоматического рефакторинга кода.
        """
        try:
            return self.analyzer.run_auto_refactor(project_path)
        except Exception as e:
            print(f"Ошибка авторефакторинга: {e}")
            return False