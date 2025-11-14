from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Set


@dataclass
class InstanceData:
    """High level parameters describing the instance."""

    name: str
    domains: int
    levels: int
    technicians: int
    interventions: int
    abandon_cost: int


@dataclass
class Technician:
    """Description of a technician and its availability."""

    identifier: int
    skills: Sequence[int]
    unavailable_days: Set[int] = field(default_factory=set)

    def is_available(self, day: int) -> bool:
        return day not in self.unavailable_days


@dataclass
class Intervention:
    """Demand that needs to be scheduled."""

    identifier: int
    duration: int
    predecessors: Sequence[int]
    priority: int
    abandon_cost: int
    requirements: Sequence[Sequence[int]]  # domain -> level -> count


@dataclass
class Assignment:
    """The actual placement of an intervention in the calendar."""

    intervention: int
    day: int
    start: int
    duration: int
    team: int

    @property
    def end_time(self) -> int:
        return self.start + self.duration


@dataclass
class DayInfo:
    """Representation of the staffing and the schedule for a single day."""

    day: int
    team_members: List[int]
    not_working: List[int]
    coverage: List[List[int]]  # domain -> level -> count
    assignments: List[Assignment] = field(default_factory=list)
    end_time: int = 0

    def schedule(self, assignment: Assignment) -> None:
        self.assignments.append(assignment)
        self.end_time = assignment.end_time


Schedule = Dict[int, Assignment]
Days = Dict[int, DayInfo]
