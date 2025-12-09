# core/business/error_handler.py

import functools
import logging
from typing import Any, Callable, TypeVar, Optional

T = TypeVar('T')
logger = logging.getLogger('ai_code_assistant')


def handle_errors(default_return: Any = None):
    """
    Декоратор для обработки ошибок в функциях
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except NameError as e:
                logger.critical(f"NameError в функции {func.__name__}: {e}")
                logger.critical("Возможно проблема с импортами или циклическими зависимостями")
                return default_return
            except Exception as e:
                logger.error(f"Ошибка в функции {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator