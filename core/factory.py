# core/factory.py

"""
Фабрика для создания и настройки всех компонентов приложения
"""

import logging
from typing import Dict, Any

from core.business.project_service import ProjectService
from core.business.code_service import CodeService
from core.business.analysis_service import IAnalysisService
from core.business.ast_service import ASTService
from core.business.code_manager import CodeManager
from core.business.change_service import ChangeManager
from core.business.project_creator_service import ProjectCreatorService, AISchemaParser
from core.business.diff_engine import DiffEngine
from core.data.project_repository import ProjectRepository
from core.business.error_handler import handle_errors

logger = logging.getLogger('ai_code_assistant')


class AppFactory:
    """Фабрика для создания компонентов приложения"""
    
    @staticmethod
    def create_all_services() -> Dict[str, Any]:
        """Создает все сервисы приложения."""
        logger.info("Создание всех сервисов приложения")
        
        # 1. Создаем репозитории
        project_repository = ProjectRepository()
        
        # 2. Создаем основные сервисы
        project_service = ProjectService(project_repository)
        code_service = CodeService(project_repository)
        
        # 3. Создаем вспомогательные сервисы
        ast_service = ASTService()
        code_manager = CodeManager()
        change_manager = ChangeManager()
        diff_engine = DiffEngine()
        project_creator = ProjectCreatorService()
        schema_parser = AISchemaParser()
        
        # 4. Создаем сервис анализа (пока мок)
        class MockAnalysisService(IAnalysisService):
            @handle_errors(default_return=[])
            def analyze_code(self, project_path: str):
                return [
                    {'type': 'info', 'message': 'Анализ начат', 'file': '', 'line': 0},
                    {'type': 'warning', 'message': 'Неиспользуемый импорт', 'file': 'main.py', 'line': 5},
                    {'type': 'error', 'message': 'Синтаксическая ошибка', 'file': 'utils.py', 'line': 10},
                    {'type': 'success', 'message': 'Анализ завершен', 'file': '', 'line': 0}
                ]
            
            @handle_errors(default_return="")
            def get_report(self, project_path: str) -> str:
                return "Отчет анализа: найдено 2 проблемы (мок-реализация)"
            
            @handle_errors(default_return=False)
            def auto_refactor(self, project_path: str) -> bool:
                return True
        
        analysis_service = MockAnalysisService()
        
        # 5. Настраиваем зависимости
        # Устанавливаем AST сервис в CodeService если поддерживает
        if hasattr(code_service, 'set_ast_service'):
            code_service.set_ast_service(ast_service)
        
        return {
            'project_repository': project_repository,
            'project_service': project_service,
            'code_service': code_service,
            'analysis_service': analysis_service,
            'ast_service': ast_service,
            'code_manager': code_manager,
            'change_manager': change_manager,
            'diff_engine': diff_engine,
            'project_creator': project_creator,
            'schema_parser': schema_parser
        }
    
    @staticmethod
    def create_for_main() -> Dict[str, Any]:
        """Создает сервисы для main.py."""
        services = AppFactory.create_all_services()
        
        logger.info("Сервисы созданы:")
        for name, service in services.items():
            logger.info(f"  - {name}: {type(service).__name__}")
        
        return services