# core/factory.py

"""
Фабрика для создания и настройки всех компонентов приложения.
Теперь использует единый AppContext.
"""

import logging
from typing import Dict, Any

from core.app_context import get_app_context, init_app_context
# Убрать некорректный импорт AISchemaParser отсюда

logger = logging.getLogger('ai_code_assistant')


class AppFactory:
    """Фабрика для создания компонентов приложения"""
    
    @staticmethod
    def create_all_services() -> Dict[str, Any]:
        """Создает все сервисы приложения через AppContext."""
        logger.info("Создание всех сервисов приложения через AppContext")
        
        # Инициализируем контекст
        if not init_app_context():
            logger.error("Не удалось инициализировать AppContext")
            return {}
        
        # Получаем все сервисы из контекста
        context = get_app_context()
        services = context.get_all_services()
        
        logger.info("Сервисы созданы через AppContext:")
        for name, service in services.items():
            logger.info(f"  - {name}: {type(service).__name__}")
        
        return services
    
    @staticmethod
    def create_for_main() -> Dict[str, Any]:
        """Создает сервисы для main.py через AppContext."""
        services = AppFactory.create_all_services()
        
        logger.info("Сервисы для main.py созданы:")
        for name, service in services.items():
            logger.info(f"  - {name}: {type(service).__name__}")
        
        return services
    
    @staticmethod
    def get_app_context():
        """Возвращает глобальный AppContext."""
        return get_app_context()