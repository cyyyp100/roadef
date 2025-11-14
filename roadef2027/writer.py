import os
from .models import Solution, SolutionModel


def write_solution(
    solution: Solution, output_dir: str, method: str = "unknown", params: dict = None
):
    # Validate solution with pydantic model
    SolutionModel(
        teams_by_day=solution.teams_by_day, interv_schedule=solution.interv_schedule
    )

    os.makedirs(output_dir, exist_ok=True)

    # build suffix from method and params
    method_str = method
    param_str = ""
    if params:
        parts = []
        for k in sorted(params.keys()):
            v = params[k]
            if v is None:
                continue
            parts.append(f"{k}-{v}")
        if parts:
            param_str = "_" + "_".join(parts)

    teams_path = os.path.join(output_dir, f"sol_teams_list_{method_str}{param_str}")
    with open(teams_path, "w") as f:
        for day, teams in solution.teams_by_day.items():
            line = f"{day} " + " ".join(
                "[" + " ".join(map(str, team)) + "]" for team in teams
            )
            f.write(line + "\n")

    interv_path = os.path.join(
        output_dir, f"sol_interventions_list_{method_str}{param_str}"
    )
    with open(interv_path, "w") as f:
        for iid, (day, start_time, team_id) in solution.interv_schedule.items():
            f.write(f"{iid} {day} {start_time} {team_id}\n")
