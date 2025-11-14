from __future__ import annotations

import argparse
import pathlib
import sys

from roadef_solver import GreedyScheduler
from roadef_solver.output import write_interventions, write_teams
from roadef_solver.parser import load_data


def _validate_input_directory(
    path: pathlib.Path,
) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Ensure that *path* points to a directory containing the three input files."""

    if not path.exists():
        raise FileNotFoundError(f"Input directory {path} does not exist")
    if not path.is_dir():
        raise NotADirectoryError(f"Input path {path} must be a directory")

    instance_path = path / "instance"
    interventions_path = path / "interv_list"
    technicians_path = path / "tech_list"

    missing = [
        str(candidate)
        for candidate in (instance_path, interventions_path, technicians_path)
        if not candidate.exists()
    ]
    if missing:
        missing_paths = ", ".join(missing)
        raise FileNotFoundError(
            "Input directory is missing required files: " f"{missing_paths}"
        )

    return instance_path, interventions_path, technicians_path


def main(argv: list[str] | None = None) -> int:
    """Parse the command line, build the schedule and write the output files."""

    parser = argparse.ArgumentParser(
        description="ROADEF 2007 greedy solver: builds a schedule and writes output files"
    )
    parser.add_argument(
        "-i",
        "--data",
        required=True,
        type=pathlib.Path,
        help=(
            "Directory containing the three ROADEF input files: 'instance', "
            "'interv_list' and 'tech_list'"
        ),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        type=pathlib.Path,
        help="Directory where the solution files will be written",
    )
    parser.add_argument(
        "--hmax",
        type=int,
        default=120,
        help="Maximum amount of work that can be scheduled in a day (default: 120)",
    )
    parser.add_argument(
        "--max-days",
        type=int,
        default=None,
        help="Optional bound on the number of days that can be explored",
    )
    args = parser.parse_args(argv)

    instance_path, interventions_path, technicians_path = _validate_input_directory(
        args.data
    )

    instance, interventions, technicians = load_data(
        instance_path, interventions_path, technicians_path
    )

    scheduler = GreedyScheduler(
        instance=instance,
        interventions=interventions,
        technicians=technicians,
        hmax=args.hmax,
        max_days=args.max_days,
    )
    schedule, days, unscheduled = scheduler.build()

    output_dir: pathlib.Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    write_teams(output_dir / "tech_teams", days)
    write_interventions(output_dir / "interv_dates", schedule)

    if unscheduled:
        message = (
            "WARNING: the following interventions could not be scheduled: "
            + ", ".join(str(value) for value in sorted(unscheduled))
        )
        print(message, file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
