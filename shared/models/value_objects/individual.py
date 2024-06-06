from typing import NamedTuple, Generic

from shared.annotations.custom import FitnessScore, UUID
from shared.models.entities.individual import T


class IndividualValue(NamedTuple, Generic[T]):
    encoding: T
    fitness: FitnessScore | None = None


class IndividualFitnessValue(NamedTuple):
    id: UUID
    fitness: FitnessScore
