from __future__ import annotations

import heapq
from typing import Dict, Iterable, List, Optional, Tuple

from .models import Assignment, DayInfo, InstanceData, Intervention, Schedule, Technician


class GreedyScheduler:
    """Simple greedy scheduler that builds a feasible plan when possible."""

    def __init__(
        self,
        instance: InstanceData,
        interventions: Dict[int, Intervention],
        technicians: Dict[int, Technician],
        hmax: int = 120,
        max_days: Optional[int] = None,
    ) -> None:
        self.instance = instance
        self.interventions = interventions
        self.technicians = technicians
        self.hmax = hmax
        self.max_days = max_days or max(365, len(interventions) * 10)
        self.schedule: Schedule = {}
        self.unscheduled: List[int] = []
        self.day_info: Dict[int, DayInfo] = {}
        self._tech_by_id = {tech.identifier: tech for tech in technicians.values()}
        self._sorted_techs = sorted(technicians.values(), key=lambda t: t.identifier)

    # ------------------------------------------------------------------
    # Planning pipeline
    # ------------------------------------------------------------------
    def build(self) -> Tuple[Schedule, Dict[int, DayInfo], List[int]]:
        order = self._topological_order()
        for identifier in order:
            intervention = self.interventions[identifier]
            if any(predecessor in self.unscheduled for predecessor in intervention.predecessors):
                self.unscheduled.append(identifier)
                continue
            assignment = self._place_intervention(intervention)
            if assignment is None:
                self.unscheduled.append(identifier)
            else:
                self.schedule[identifier] = assignment
        return self.schedule, self.day_info, self.unscheduled

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _topological_order(self) -> List[int]:
        graph: Dict[int, List[int]] = {identifier: [] for identifier in self.interventions}
        indegree: Dict[int, int] = {identifier: 0 for identifier in self.interventions}
        for intervention in self.interventions.values():
            for predecessor in intervention.predecessors:
                graph.setdefault(predecessor, []).append(intervention.identifier)
                indegree[intervention.identifier] += 1
        queue: List[Tuple[int, int]] = []
        for identifier, degree in indegree.items():
            if degree == 0:
                heapq.heappush(queue, (self.interventions[identifier].priority, identifier))
        order: List[int] = []
        while queue:
            priority, identifier = heapq.heappop(queue)
            order.append(identifier)
            for successor in graph.get(identifier, []):
                indegree[successor] -= 1
                if indegree[successor] == 0:
                    heapq.heappush(queue, (self.interventions[successor].priority, successor))
        if len(order) != len(self.interventions):
            remaining = set(self.interventions) - set(order)
            order.extend(sorted(remaining))
        return order

    def _ready_time(self, intervention: Intervention) -> Tuple[int, int]:
        if not intervention.predecessors:
            return 1, 0
        ready_day = 1
        ready_time = 0
        for predecessor in intervention.predecessors:
            assignment = self.schedule.get(predecessor)
            if assignment is None:
                continue
            finish_day = assignment.day
            finish_time = assignment.end_time
            if finish_day > ready_day:
                ready_day = finish_day
                ready_time = finish_time
            elif finish_day == ready_day:
                ready_time = max(ready_time, finish_time)
        return ready_day, ready_time

    def _place_intervention(self, intervention: Intervention) -> Optional[Assignment]:
        ready_day, ready_time = self._ready_time(intervention)
        duration = intervention.duration
        day = max(1, ready_day)
        while day <= self.max_days:
            info = self._ensure_day(day)
            if not self._team_satisfies(info.coverage, intervention.requirements):
                day += 1
                continue
            team_members = self._select_team(info, intervention.requirements)
            if team_members is None:
                day += 1
                continue
            team_id = info.register_team(team_members)
            start_time = info.end_time
            if day == ready_day:
                start_time = max(start_time, ready_time)
            if start_time + duration <= self.hmax:
                assignment = Assignment(
                    intervention=intervention.identifier,
                    day=day,
                    start=start_time,
                    duration=duration,
                    team=team_id,
                )
                info.schedule(assignment)
                return assignment
            day += 1
        return None

    def _ensure_day(self, day: int) -> DayInfo:
        if day in self.day_info:
            return self.day_info[day]
        team_members: List[int] = []
        not_working: List[int] = []
        for technician in self._sorted_techs:
            if technician.is_available(day):
                team_members.append(technician.identifier)
            else:
                not_working.append(technician.identifier)
        coverage = self._compute_coverage(team_members)
        info = DayInfo(
            day=day,
            team_members=team_members,
            not_working=not_working,
            coverage=coverage,
        )
        self.day_info[day] = info
        return info

    def _compute_coverage(self, team: Iterable[int]) -> List[List[int]]:
        coverage = [
            [0 for _ in range(self.instance.levels)]
            for _ in range(self.instance.domains)
        ]
        for identifier in team:
            technician = self._tech_by_id[identifier]
            for domain, level in enumerate(technician.skills):
                effective_level = min(max(level, 0), self.instance.levels)
                for threshold in range(1, effective_level + 1):
                    coverage[domain][threshold - 1] += 1
        return coverage

    def _team_satisfies(
        self,
        coverage: List[List[int]],
        requirements: Iterable[Iterable[int]],
    ) -> bool:
        for domain, domain_requirements in enumerate(requirements):
            if domain >= len(coverage):
                if any(required > 0 for required in domain_requirements):
                    return False
                continue
            for level, required in enumerate(domain_requirements):
                if level >= len(coverage[domain]):
                    if required > 0:
                        return False
                    continue
                if coverage[domain][level] < required:
                    return False
        return True

    def _select_team(
        self,
        info: DayInfo,
        requirements: Iterable[Iterable[int]],
    ) -> Optional[List[int]]:
        matrix = [list(domain) for domain in requirements]
        if not matrix:
            return []
        if all(all(required == 0 for required in domain) for domain in matrix):
            return []
        coverage = [
            [0 for _ in range(self.instance.levels)]
            for _ in range(self.instance.domains)
        ]
        selected: List[int] = []

        def meets_requirements() -> bool:
            for domain, domain_requirements in enumerate(matrix):
                for level, required in enumerate(domain_requirements):
                    if level >= len(coverage[domain]):
                        if required > 0:
                            return False
                        continue
                    if coverage[domain][level] < required:
                        return False
            return True

        for identifier in info.team_members:
            technician = self._tech_by_id[identifier]
            contributes = False
            for domain, level in enumerate(technician.skills):
                effective_level = min(max(level, 0), self.instance.levels)
                for threshold in range(1, effective_level + 1):
                    index = threshold - 1
                    if index >= len(coverage[domain]):
                        continue
                    if domain >= len(matrix) or index >= len(matrix[domain]):
                        continue
                    if coverage[domain][index] < matrix[domain][index]:
                        coverage[domain][index] += 1
                        contributes = True
            if contributes:
                selected.append(identifier)
                if meets_requirements():
                    break

        if meets_requirements():
            return selected

        if info.team_members:
            return list(info.team_members)
        return None


__all__ = ["GreedyScheduler"]
