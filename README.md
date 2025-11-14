# ROADEF Greedy Scheduler

This repository provides a lightweight greedy scheduler that can build a feasible
solution for the simplified ROADEF/EURO Challenge maintenance planning problem
used in teaching assignments.

## Overview

The solver parses the three input files describing the instance, the
interventions and the technicians, and produces two output files:

* `tech_teams` — composition of the working team for every day.
* `interv_dates` — start date and time for every scheduled intervention.

The current implementation keeps a single team per day containing all available
technicians. Interventions are processed in a topological order that honours
predecessor constraints and prefers higher priority jobs. For each intervention
we pick the earliest day and start time that provide enough skills and respect
both the daily workload limit and the precedence constraints.

Interventions that cannot be placed (because the required skills are never
available on the same day or because the daily time limit would be exceeded)
are reported on the standard error stream. Already unscheduled predecessors also
cause the dependent interventions to be skipped.

## Usage

```bash
python solve.py <instance> <interv_list> <tech_list> [--output out_dir]
```

Optional arguments:

* `--output`: directory where the two solution files are written (default: current directory)
* `--hmax`: maximum work per day (default: 120)
* `--max-days`: explicit bound on the explored number of days (defaults to `max(365, len(interventions) * 10)`)

The solver writes `tech_teams` and `interv_dates` in the requested directory.
If some interventions could not be scheduled, they are listed in a warning on
stderr.
