# gui/utils/event_bus.py

class EventBus:
    """
    Простая и расширяемая реализация шины событий (Event Bus) для GUI, контроллеров и сервисов.
    Позволяет подписываться на события, отписываться, рассылать публикации.
    """

    def __init__(self):
        # Словарь: имя события -> список handler-ов
        self._subscribers = {}

    def subscribe(self, event_name, handler):
        """
        Подписать обработчик (функцию) на событие.
        handler(event_name, *args, **kwargs)
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)

    def unsubscribe(self, event_name, handler):
        """
        Отписать обработчик от события.
        """
        handlers = self._subscribers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)
            if not handlers:
                del self._subscribers[event_name]

    def publish(self, event_name, *args, **kwargs):
        """
        Вызвать все обработчики события с заданными параметрами.
        """
        handlers = self._subscribers.get(event_name, [])
        for handler in handlers:
            handler(event_name, *args, **kwargs)

    def clear(self):
        """
        Удалить все подписки (например при завершении/перезапуске).
        """
        self._subscribers.clear()

    def get_subscribers(self, event_name):
        """
        Получить список подписчиков на событие.
        """
        return self._subscribers.get(event_name, [])

    def has_subscribers(self, event_name):
        """
        Есть ли хоть один подписчик на данное событие.
        """
        return bool(self._subscribers.get(event_name))