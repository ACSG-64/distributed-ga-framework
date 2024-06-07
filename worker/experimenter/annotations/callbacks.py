from typing import TypeAlias, Callable, List, TypeVar

from shared.models.entities.individual import IndividualEntity

T = TypeVar('T')

NextCallback: TypeAlias = Callable[[List[IndividualEntity[T]]], any]
