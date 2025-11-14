from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Optional

from . import parser
from .output import write_interventions, write_teams
from .scheduler import GreedyScheduler


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def build_argument_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Greedy scheduler for the ROADEF challenge TP")
    ap.add_argument("instance", type=pathlib.Path, help="Path to the instance description file")
    ap.add_argument("interventions", type=pathlib.Path, help="Path to the interventions list file")
    ap.add_argument("technicians", type=pathlib.Path, help="Path to the technicians list file")
    ap.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="Directory where the solution files will be written",
    )
    ap.add_argument(
        "--hmax",
        type=_positive_int,
        default=120,
        help="Maximum amount of work that can be scheduled in a day (default: 120)",
    )
    ap.add_argument(
        "--max-days",
        type=_positive_int,
        default=None,
        help="Upper bound on the number of days that can be explored",
    )
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    args = build_argument_parser().parse_args(argv)
    output_dir: pathlib.Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    instance, interventions, technicians = parser.load_data(
        args.instance, args.interventions, args.technicians
    )

    scheduler = GreedyScheduler(
        instance=instance,
        interventions=interventions,
        technicians=technicians,
        hmax=args.hmax,
        max_days=args.max_days,
    )
    schedule, days, unscheduled = scheduler.build()

    teams_path = output_dir / "tech_teams"
    interventions_path = output_dir / "interv_dates"
    write_teams(teams_path, days)
    write_interventions(interventions_path, schedule)

    if unscheduled:
        message = (
            f"WARNING: the following interventions could not be scheduled: "
            f"{', '.join(str(value) for value in sorted(unscheduled))}"
        )
        print(message, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
