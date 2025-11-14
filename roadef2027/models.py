from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from pydantic import BaseModel, validator, model_validator

# ------------------
# Dataclasses (core data containers)
# ------------------


@dataclass
class Technician:
    id: int
    levels: Dict[int, int]
    unavailable_days: List[int] = field(default_factory=list)


@dataclass
class Intervention:
    id: int
    duration: int
    preds: List[int]
    priority: int
    cost: int
    requirements: Dict[int, Dict[int, int]]


@dataclass
class Instance:
    name: str
    n_domains: int
    n_levels: int
    n_techs: int
    n_interv: int
    abandon_cost: int
    technicians: List[Technician]
    interventions: List[Intervention]
    HMAX: int = 120


@dataclass
class Solution:
    teams_by_day: Dict[int, List[List[int]]]
    interv_schedule: Dict[int, Tuple[int, int, int]]


# ------------------
# Pydantic Models (validation)
# ------------------


class TechnicianModel(BaseModel):
    id: int
    levels: Dict[int, int]
    unavailable_days: List[int] = []

    @validator("id")
    def id_non_negative(cls, v):
        if v < 0:
            raise ValueError("Technician id must be non-negative")
        return v

    @validator("levels")
    def levels_non_negative(cls, v):
        for d, lvl in v.items():
            if lvl < 0:
                raise ValueError(f"Domain {d}: level must be non-negative")
        return v


class InterventionModel(BaseModel):
    id: int
    duration: int
    preds: List[int]
    priority: int
    cost: int
    requirements: Dict[int, Dict[int, int]]

    @validator("duration", "priority", "cost")
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("Must be non-negative")
        return v


class InstanceModel(BaseModel):
    name: str
    n_domains: int
    n_levels: int
    n_techs: int
    n_interv: int
    abandon_cost: int
    technicians: List[TechnicianModel]
    interventions: List[InterventionModel]

    @validator("n_domains", "n_levels", "n_techs", "n_interv", "abandon_cost")
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("must be non-negative")
        return v


def no_scheduled_intervention_by_non_working_team(model):
    # Check interv_schedule: the second element is assumed to be the team id (if present)
    interv_schedule = getattr(model, "interv_schedule", {}) or {}
    for interv_id, sched in interv_schedule.items():
        if len(sched) > 1 and sched[1] == 0:
            raise ValueError(
                f"Intervention {interv_id} is scheduled with non-working team 0"
            )
    return model


class SolutionModel(BaseModel):
    instance_model: InstanceModel
    teams_by_day: Dict[int, List[List[int]]]
    interv_schedule: Dict[int, Tuple[int, int, int]]

    @model_validator(mode="after")
    def placeholder_constraints(cls, model):
        no_scheduled_intervention_by_non_working_team(model)
        # Placeholder: no real feasibility checks implemented yet
        # This is where skill/precedence checks could be added
        return model
