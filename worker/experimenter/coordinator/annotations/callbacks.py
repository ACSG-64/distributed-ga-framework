from typing import TypeAlias, Callable, List, TypeVar

from shared.models.entities.individual import IndividualEntity
from worker.experimenter.annotations.callbacks import NextCallback

T = TypeVar('T')

OnSampleReadyCallback: TypeAlias = Callable[[List[IndividualEntity[T]], NextCallback], any]
OnEvaluationCompleteCb: TypeAlias = NextCallback
