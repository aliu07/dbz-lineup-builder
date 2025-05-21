from dataclasses import dataclass, field
from models.paddler import Paddler

@dataclass
class Boat:
    id: int
    capacity_per_side: int
    right: list[Paddler] = field(default_factory=list)
    left: list[Paddler] = field(default_factory=list)

@dataclass
class SmallBoat(Boat):
    def __init__(self, id: int):
        super().__init__(id=id, capacity_per_side=5)

@dataclass
class StandardBoat(Boat):
    def __init__(self, id: int):
        super().__init__(id=id, capacity_per_side=10)
