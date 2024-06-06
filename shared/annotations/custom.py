from typing import TypeAlias

UUID: TypeAlias = int | str
FitnessScore: TypeAlias = float | int

IndividualEncoding: TypeAlias = list[list[float | int]]
Genome: TypeAlias = list[list[float | int]]
