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

* comment lire output : 
Lire tech_teams
Ce fichier commence par un en-tête day not_working team1 ... teamN. Chaque ligne suivante correspond à une journée :

day : numéro du jour dans le planning.

not_working : liste (entre crochets) des techniciens sans affectation ce jour-là.

team1, team2, … : membres de chaque équipe utilisée ce jour-là (toujours au format liste). Les colonnes vides n’apparaissent pas si aucune équipe n’est créée, et le nombre de colonnes dépend du maximum d’équipes mobilisées sur une journée donnée.

Exemple : 3 [4 7] [1 2] [3] signifie jour 3, techniciens 4 et 7 inactifs, équipe 1 composée des techniciens 1 et 2, équipe 2 du technicien 3.

Lire interv_dates
Ce fichier liste les interventions planifiées, avec un en-tête interv day time team. Chaque ligne suivante contient :

interv : identifiant de l’intervention.

day : jour où elle commence.

time : heure de début (en minutes depuis le début de la journée).

team : identifiant de l’équipe affectée (correspondant aux colonnes du fichier tech_teams).

Si une intervention n’est pas planifiée, son identifiant est signalé dans la sortie d’erreur standard après l’exécution de la commande.

* `--hmax`: maximum work per day (default: 120)
* `--max-days`: explicit bound on the explored number of days (defaults to `max(365, len(interventions) * 10)`)

The solver writes `tech_teams` and `interv_dates` in the requested directory.
If some interventions could not be scheduled, they are listed in a warning on
stderr.
