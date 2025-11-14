from __future__ import annotations

import pathlib
from typing import Dict, Iterable, List

from .models import Assignment, DayInfo


def _format_list(values: Iterable[int]) -> str:
    values = list(values)
    if not values:
        return "[]"
    return "[" + " ".join(str(value) for value in values) + "]"


def write_teams(path: pathlib.Path, days: Dict[int, DayInfo]) -> None:
    max_teams = max((len(info.teams) for info in days.values()), default=0)
    header = ["day", "not_working"] + [f"team{i}" for i in range(1, max_teams + 1)]
    lines: List[str] = [" ".join(header)]
    for day in sorted(days):
        info = days[day]
        values = [str(day), _format_list(info.not_working)]
        for team_id in range(1, max_teams + 1):
            members = info.teams.get(team_id, [])
            values.append(_format_list(members))
        lines.append(" ".join(values))
    path.write_text("\n".join(lines) + "\n")


def write_interventions(path: pathlib.Path, assignments: Dict[int, Assignment]) -> None:
    lines: List[str] = ["interv day time team"]
    for identifier in sorted(assignments):
        assignment = assignments[identifier]
        line = f"{assignment.intervention} {assignment.day} {assignment.start} {assignment.team}"
        lines.append(line)
    path.write_text("\n".join(lines) + "\n")
