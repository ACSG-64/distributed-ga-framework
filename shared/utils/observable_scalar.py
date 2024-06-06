from typing import TypeVar, Generic, Callable

from shared.utils.event_listener import EventListener

T = TypeVar('T')


class ObservableScalar(Generic[T]):
    def __init__(self, initial_value):
        self._value = initial_value
        self._cached = None
        self._observers = EventListener()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_val: T):
        if new_val == self._value:
            return
        self._cached = self._value
        self._value = new_val
        self._observers(self._value, self._cached)

    def observe(self, fn: Callable[[T, T], any], trigger_now=False):
        self._observers.add_listener(fn)
        if trigger_now:
            self._observers(self._value, self._cached)

    def remove_observers(self):
        self._observers.remove_listeners()
