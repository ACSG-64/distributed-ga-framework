from typing import TypeAlias, Callable, List, TypeVar

from coordinator.experimenter.annotations.callbacks import NextCallback, StopCallback

from shared.models.entities.individual import IndividualEntity

T = TypeVar('T')

CreateNewGenerationCallback: TypeAlias = Callable[
    [List[IndividualEntity[T]], NextCallback[T], StopCallback], any]
OnTestingPopReadyCb: TypeAlias = Callable[[List[IndividualEntity[T]]], any]
OnPopulationTestedCb: TypeAlias = Callable[[List[IndividualEntity[T]]], any]
