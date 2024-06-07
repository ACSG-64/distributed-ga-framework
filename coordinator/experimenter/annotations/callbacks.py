from typing import TypeAlias, Callable, List, TypeVar

from shared.models.value_objects.individual import IndividualValue

T = TypeVar('T')

NextCallback: TypeAlias = Callable[[List[IndividualValue[T]]], None]
StopCallback: TypeAlias = Callable[[], None]
