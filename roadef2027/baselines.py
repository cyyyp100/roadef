import random
from typing import Dict, List, Tuple
from .models import Instance, Solution


def random_baseline(instance: Instance, seed: int = None) -> Solution:
    if seed is not None:
        random.seed(seed)

    teams_by_day: Dict[int, List[List[int]]] = {}
    interv_schedule: Dict[int, Tuple[int, int, int]] = {}

    # Assign all techs to team 1 for simplicity
    teams_by_day[0] = [[], list(range(1, instance.n_techs + 1))]

    for interv in instance.interventions:
        day = random.randint(0, 10)
        start_time = random.randint(0, max(0, instance.HMAX - interv.duration))
        team_id = 1
        interv_schedule[interv.id] = (day, start_time, team_id)

    return Solution(teams_by_day, interv_schedule, instance_model=instance)
