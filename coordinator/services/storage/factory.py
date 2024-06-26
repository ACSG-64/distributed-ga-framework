from enum import Enum
from typing import TypeVar, Generic

from coordinator.services.storage.interfaces.istorage import IStorage

T = TypeVar('T')


class StorageDrivers(Enum):
    SQLITE = 1
    MEMORY = 2


class StorageFactory(Generic[T]):

    @classmethod
    def create(cls, driver: StorageDrivers, **kwargs) -> IStorage[T]:
        if driver == StorageDrivers.SQLITE:
            from coordinator.services.storage.implementations.sqlite.sqlite import SqliteStorage
            return SqliteStorage[T](**kwargs)
        else:
            from coordinator.services.storage.implementations.in_memory import InMemoryStorage
            return InMemoryStorage[T]()
