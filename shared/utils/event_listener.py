from typing import Generic, TypeVar, List

T = TypeVar('T')


class EventListener(Generic[T]):
    def __init__(self):
        self.listeners: List[T] = []

    def __call__(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)

    def add_listener(self, listener: T):
        self.listeners.append(listener)

    def remove_listeners(self):
        self.listeners.clear()
