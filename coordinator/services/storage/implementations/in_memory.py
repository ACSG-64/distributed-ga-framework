from typing import TypeVar

from coordinator.services.storage.implementations.sqlite.sqlite import SqliteStorage

T = TypeVar('T')


class InMemoryStorage(SqliteStorage[T]):
    def __init__(self):
        super().__init__(':memory:')
