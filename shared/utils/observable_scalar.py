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
        """
        Returns the actual value
        :return:
        """
        return self._value

    @value.setter
    def value(self, new_val: T):
        """
        Sets the new value and notifies the observers if the new value is different to the previous onw
        :param new_val:
        """
        if new_val == self._value:
            return
        self._cached = self._value
        self._value = new_val
        self._observers(self._value, self._cached)

    def observe(self, callback: Callable[[T, T], any], trigger_now=False):
        """
        Calls the observer when the value is changed
        :param callback: receives two parameters, the first one is the changed value and the second is the previous value
        :param trigger_now: True if the callback should be triggered immediately
        """
        self._observers.add_listener(callback)
        if trigger_now:
            self._observers(self._value, self._cached)

    def remove_observers(self):
        self._observers.remove_listeners()
