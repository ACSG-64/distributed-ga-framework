from enum import Enum
from typing import Generic, TypeVar, Callable

from shared.utils.event_listener import EventListener

T = TypeVar('T')


class PromiseStatus(Enum):
    PENDING = 1
    FULFILLED = 2
    REJECTED = 3


class Promise(Generic[T]):
    """
    An utility similar to their JavaScript counterpart, useful to return data on asynchronous cases
    where the data will be available at a later time
    """
    def __init__(self):
        self._status = PromiseStatus.PENDING
        self._value: T | None = None
        self._then_cb = EventListener()
        self._catch_cb = EventListener()

    @property
    def status(self):
        return self._status

    @property
    def value(self):
        """
        The initial value is None. If the expected value is None, check whether the promise has
        been fulfilled
        :return: The value
        """
        return self._value

    @property
    def handlers(self):
        """
        :return: Resolve function, reject function
        """
        return self.__resolve, self.__reject

    def then(self, callback: Callable[[T], any]):
        """
        :param callback: A listener to be called when the promise fulfills. The resolved value
        will be provided
        """
        if self._status == PromiseStatus.FULFILLED:
            callback(self._value)
            self._then_cb.remove_listeners()
        else:
            self._then_cb.add_listener(callback)
        return self

    def catch(self, callback: Callable[[any], any]):
        """
        A listener to be called when the promise is rejected. The exception or error value
        will be provided
        :param callback:
        :return:
        """
        if self._status == PromiseStatus.REJECTED:
            callback(self._value)
            self._catch_cb.remove_listeners()
        else:
            self._catch_cb.add_listener(callback)
        return self

    def __resolve(self, value: T):
        self._value = value
        self._status = PromiseStatus.FULFILLED
        self._then_cb(self._value)

    def __reject(self, value):
        self._value = value
        self._status = PromiseStatus.REJECTED
        self._catch_cb(self._value)
