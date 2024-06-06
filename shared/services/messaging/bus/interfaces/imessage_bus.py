from abc import ABC, abstractmethod

from shared.services.messaging.interfaces.icontrols import IMessagingControls


class IMessageBusControls(IMessagingControls, ABC):
    """
    Basic controls for message buses
    """
    @abstractmethod
    def pause(self):
        """
        Pauses the reception of new messages
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def resume(self):
        """
        Resumes the reception of messages
        :return:
        """
        raise NotImplementedError
