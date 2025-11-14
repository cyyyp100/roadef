from __future__ import annotations

import pathlib
from typing import Dict, List

from .models import InstanceData, Intervention, Technician


def _parse_int_list(raw: str) -> List[int]:
    raw = raw.strip()
    if not raw:
        return []
    if raw[0] != "[" or raw[-1] != "]":
        raise ValueError(f"Expected list enclosed in brackets, got: {raw!r}")
    content = raw[1:-1].strip()
    if not content:
        return []
    return [int(token) for token in content.replace(",", " ").split()]


def _extract_list_segment(line: str) -> (str, str, str):
    start = line.find("[")
    if start == -1:
        raise ValueError(f"Expected '[' in line: {line}")
    depth = 0
    for idx in range(start, len(line)):
        if line[idx] == "[":
            depth += 1
        elif line[idx] == "]":
            depth -= 1
            if depth == 0:
                end = idx
                break
    else:
        raise ValueError(f"Unbalanced brackets in line: {line}")
    prefix = line[:start].strip()
    segment = line[start : end + 1]
    suffix = line[end + 1 :].strip()
    return prefix, segment, suffix


def parse_instance(path: pathlib.Path) -> InstanceData:
    tokens = path.read_text().split()
    if len(tokens) < 6:
        raise ValueError("Instance file must contain six tokens")
    name = tokens[0]
    domains, levels, techs, interventions, abandon_cost = map(int, tokens[1:6])
    return InstanceData(
        name=name,
        domains=domains,
        levels=levels,
        technicians=techs,
        interventions=interventions,
        abandon_cost=abandon_cost,
    )


def parse_interventions(path: pathlib.Path, instance: InstanceData) -> Dict[int, Intervention]:
    interventions: Dict[int, Intervention] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        prefix, segment, suffix = _extract_list_segment(line)
        prefix_tokens = prefix.split()
        if len(prefix_tokens) < 2:
            raise ValueError(f"Invalid intervention header: {raw_line}")
        identifier = int(prefix_tokens[0])
        duration = int(prefix_tokens[1])
        predecessors = _parse_int_list(segment)
        suffix_tokens = suffix.split()
        if len(suffix_tokens) < 2 + instance.domains * instance.levels:
            raise ValueError(f"Insufficient data for intervention {identifier}")
        priority = int(suffix_tokens[0])
        abandon_cost = int(suffix_tokens[1])
        requirement_tokens = [int(token) for token in suffix_tokens[2 : 2 + instance.domains * instance.levels]]
        requirements: List[List[int]] = []
        index = 0
        for _domain in range(instance.domains):
            levels = []
            for _level in range(instance.levels):
                levels.append(requirement_tokens[index])
                index += 1
            requirements.append(levels)
        interventions[identifier] = Intervention(
            identifier=identifier,
            duration=duration,
            predecessors=predecessors,
            priority=priority,
            abandon_cost=abandon_cost,
            requirements=requirements,
        )
    return interventions


def parse_technicians(path: pathlib.Path, instance: InstanceData) -> Dict[int, Technician]:
    technicians: Dict[int, Technician] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        prefix, segment, _ = _extract_list_segment(line)
        tokens = prefix.split()
        if len(tokens) < 1 + instance.domains:
            raise ValueError(f"Invalid technician line: {raw_line}")
        identifier = int(tokens[0])
        skills = [int(token) for token in tokens[1 : 1 + instance.domains]]
        unavailable_days = set(_parse_int_list(segment))
        technicians[identifier] = Technician(
            identifier=identifier,
            skills=skills,
            unavailable_days=unavailable_days,
        )
    return technicians


def ensure_consistency(interventions: Dict[int, Intervention], technicians: Dict[int, Technician], instance: InstanceData) -> None:
    if len(interventions) != instance.interventions:
        raise ValueError(
            f"Expected {instance.interventions} interventions but found {len(interventions)} in the list"
        )
    if len(technicians) != instance.technicians:
        raise ValueError(
            f"Expected {instance.technicians} technicians but found {len(technicians)} in the list"
        )
    all_ids = set(interventions.keys())
    for intervention in interventions.values():
        for predecessor in intervention.predecessors:
            if predecessor not in all_ids:
                raise ValueError(
                    f"Intervention {intervention.identifier} references unknown predecessor {predecessor}"
                )


def load_data(
    instance_path: pathlib.Path,
    interventions_path: pathlib.Path,
    technicians_path: pathlib.Path,
) -> tuple[InstanceData, Dict[int, Intervention], Dict[int, Technician]]:
    instance = parse_instance(instance_path)
    interventions = parse_interventions(interventions_path, instance)
    technicians = parse_technicians(technicians_path, instance)
    ensure_consistency(interventions, technicians, instance)
    return instance, interventions, technicians
