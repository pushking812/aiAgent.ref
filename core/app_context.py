# core/app_context.py

"""
Централизованный контекст приложения для управления зависимостями.
Устраняет дублирование создания сервисов в разных местах.
"""

import logging
from typing import Dict, Any

from core.business.project_service import ProjectService
from core.business.code_service import CodeService
from core.business.analysis_service import IAnalysisService
from core.business.ast_service import ASTService
from core.business.code_manager import CodeManager
from core.business.change_service import ChangeManager
from core.business.project_creator_service import ProjectCreatorService
from core.business.ai_schema_service import AISchemaService  # Используем новый сервис
from core.business.diff_engine import DiffEngine
from core.data.project_repository import ProjectRepository
from core.business.error_handler import handle_errors

logger = logging.getLogger('ai_code_assistant')

class AppContext:
    """Контекст приложения с единым управлением зависимостями"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
        logger.debug("Создан AppContext")
    
    def initialize(self) -> bool:
        """Инициализирует все сервисы приложения"""
        if self._initialized:
            return True
        
        try:
            logger.info("Инициализация AppContext...")
            
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
            ai_schema_service = AISchemaService()
            
            # 4. Создаем AISchemaParser для обратной совместимости
            from core.data.ai_schema_parser import AISchemaParser
            schema_parser = AISchemaParser()
            
            # 5. Создаем сервис анализа (мок-реализация)
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
            
            # 6. Создаем сервис структуры проекта
            from core.business.project_structure_service import ProjectStructureService
            project_structure_service = ProjectStructureService(project_repository, ast_service)
            
            # Сохраняем все сервисы
            self._services = {
                'project_repository': project_repository,
                'project_service': project_service,
                'code_service': code_service,
                'analysis_service': analysis_service,
                'ast_service': ast_service,
                'code_manager': code_manager,
                'change_manager': change_manager,
                'diff_engine': diff_engine,
                'project_creator': project_creator,
                'ai_schema_service': ai_schema_service,
                'project_structure_service': project_structure_service,
                'schema_parser': schema_parser
            }
            
            self._initialized = True
            logger.info("AppContext инициализирован успешно")
            logger.info("Сервисы созданы:")
            for name, service in self._services.items():
                logger.info(f"  - {name}: {type(service).__name__}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации AppContext: {e}")
            return False
    
    def get_service(self, service_name: str) -> Any:
        """Возвращает сервис по имени"""
        if not self._initialized:
            self.initialize()
        
        if service_name in self._services:
            return self._services[service_name]
        
        logger.error(f"Сервис '{service_name}' не найден в контексте")
        return None
    
    def get_all_services(self) -> Dict[str, Any]:
        """Возвращает все сервисы"""
        if not self._initialized:
            self.initialize()
        
        return self._services.copy()
    
    def set_service(self, service_name: str, service: Any) -> None:
        """Устанавливает сервис в контекст"""
        self._services[service_name] = service
        logger.debug(f"Сервис '{service_name}' установлен в контекст")
    
    def get_project_repository(self) -> ProjectRepository:
        """Возвращает репозиторий проекта"""
        return self.get_service('project_repository')
    
    def get_project_service(self) -> ProjectService:
        """Возвращает сервис проекта"""
        return self.get_service('project_service')
    
    def get_code_service(self) -> CodeService:
        """Возвращает сервис кода"""
        return self.get_service('code_service')
    
    def get_analysis_service(self) -> IAnalysisService:
        """Возвращает сервис анализа"""
        return self.get_service('analysis_service')
    
    def get_ast_service(self) -> ASTService:
        """Возвращает AST сервис"""
        return self.get_service('ast_service')
    
    def get_code_manager(self) -> CodeManager:
        """Возвращает менеджер кода"""
        return self.get_service('code_manager')
    
    def get_change_manager(self) -> ChangeManager:
        """Возвращает менеджер изменений"""
        return self.get_service('change_manager')
    
    def get_diff_engine(self) -> DiffEngine:
        """Возвращает движок сравнения"""
        return self.get_service('diff_engine')
    
    def get_project_creator(self) -> ProjectCreatorService:
        """Возвращает создатель проектов"""
        return self.get_service('project_creator')
    
    def get_ai_schema_service(self) -> AISchemaService:
        """Возвращает сервис AI схем"""
        return self.get_service('ai_schema_service')
    
    def clear(self):
        """Очищает контекст"""
        self._services.clear()
        self._initialized = False
        logger.debug("AppContext очищен")

    def get_schema_parser(self):
        """Возвращает AISchemaParser для обратной совместимости"""
        return self.get_service('schema_parser')

# Глобальный экземпляр контекста
_app_context: AppContext = None

def get_app_context() -> AppContext:
    """Возвращает глобальный экземпляр AppContext"""
    global _app_context
    if _app_context is None:
        _app_context = AppContext()
    return _app_context

def init_app_context() -> bool:
    """Инициализирует глобальный контекст приложения"""
    context = get_app_context()
    return context.initialize()
    