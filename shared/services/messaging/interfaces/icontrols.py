from abc import ABC, abstractmethod
from typing import Callable


class IMessagingControls(ABC):
    """
    Basic controls for any message services such as message buses, pubsub, and so on
    """

    @property
    @abstractmethod
    def is_listening(self) -> bool:
        """
        Check whether it is listening
        :return: True if it is listening, otherwise False
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Check whether it is stopped.
        :return: True if it is listening, otherwise False
        """
        raise NotImplementedError

    @abstractmethod
    def listen(self, callback: Callable[[], any] | None = None):
        """
        :param callback: Will be triggered as soon as it starts listening
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError
