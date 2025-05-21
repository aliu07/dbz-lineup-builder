from dataclasses import dataclass

@dataclass(frozen=True)
class Paddler:
    id: int
    name: str
    weight: float
    gender: str
    side: str
