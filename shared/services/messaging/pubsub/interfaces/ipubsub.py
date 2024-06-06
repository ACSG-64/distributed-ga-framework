from abc import ABC

from shared.services.messaging.interfaces.icontrols import IMessagingControls


class IPubSubControls(IMessagingControls, ABC):
    pass
