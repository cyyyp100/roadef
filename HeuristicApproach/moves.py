import random

HMAX = 120


# =================================================================
# Utilitaires de copie (deep-copy sûre)
# =================================================================
def deep_copy_schedule(schedule):
    """Deep copy du planning complet : jours → équipes → listes."""
    return {
        day: [list(team) for team in schedule[day]]
        for day in schedule
    }


def copy_day(solution, day):
    """Copie profonde d’un jour uniquement."""
    return [list(team) for team in solution["schedule"][day]]


def copy_start_end(solution):
    return solution["start"].copy(), solution["end"].copy()


# =================================================================
# Recalcule les horaires pour UN jour, annule le move si impossible
# =================================================================
def recompute_times_for_day_safe(solution, day, data):
    durations = data["duration"]
    pred = data["pred"]

    start = solution["start"]
    end = solution["end"]

    day_start = day * HMAX
    day_end = (day + 1) * HMAX

    for team_seq in solution["schedule"][day]:
        current_time = day_start

        # IMPORTANT : ne jamais enlever les interventions → move annulé si problème
        for I in team_seq:
            duration = durations[I]
            preds = pred.get(I, [])

            earliest_pred = max(end.get(p, 0) for p in preds) if preds else day_start

            s = max(current_time, earliest_pred)
            e = s + duration

            # Débordement interdit → échec du move
            if e > day_end:
                return False

            start[I] = s
            end[I] = e
            current_time = e

    return True


# =================================================================
# Évite les moves qui ne changent rien
# =================================================================
def is_same_day(sol1, sol2, day):
    return sol1["schedule"][day] == sol2["schedule"][day]


# =================================================================
# MOVE 1 : échanger deux interventions dans une même équipe
# =================================================================
def move_reorder(solution, day, data):
    sched = solution["schedule"]

    if day not in sched or len(sched[day]) <= 1:
        return solution

    new_sol = {
        "teams": solution["teams"],
        "schedule": deep_copy_schedule(solution["schedule"]),
        "start": solution["start"].copy(),
        "end": solution["end"].copy(),
    }

    # choisir une équipe (≠ équipe 0)
    team_idx = random.randrange(1, len(new_sol["schedule"][day]))
    seq = new_sol["schedule"][day][team_idx]

    if len(seq) < 2:
        return solution

    i, j = random.sample(range(len(seq)), 2)
    seq[i], seq[j] = seq[j], seq[i]

    if not recompute_times_for_day_safe(new_sol, day, data):
        return solution

    if is_same_day(solution, new_sol, day):
        return solution

    return new_sol


# =================================================================
# MOVE 2 : échanger une intervention entre équipes du même jour
# =================================================================
def move_swap_between_teams(solution, day, data):
    sched = solution["schedule"]

    if day not in sched or len(sched[day]) <= 2:
        return solution

    new_sol = {
        "teams": solution["teams"],
        "schedule": deep_copy_schedule(solution["schedule"]),
        "start": solution["start"].copy(),
        "end": solution["end"].copy(),
    }

    valid = list(range(1, len(new_sol["schedule"][day])))
    t1, t2 = random.sample(valid, 2)

    if not new_sol["schedule"][day][t1] or not new_sol["schedule"][day][t2]:
        return solution

    i = random.randrange(len(new_sol["schedule"][day][t1]))
    j = random.randrange(len(new_sol["schedule"][day][t2]))

    new_sol["schedule"][day][t1][i], new_sol["schedule"][day][t2][j] = \
        new_sol["schedule"][day][t2][j], new_sol["schedule"][day][t1][i]

    if not recompute_times_for_day_safe(new_sol, day, data):
        return solution

    if is_same_day(solution, new_sol, day):
        return solution

    return new_sol


# =================================================================
# MOVE 3 : déplacer une intervention d’une équipe vers une autre
# =================================================================
def move_shift(solution, day, data):
    sched = solution["schedule"]

    if day not in sched or len(sched[day]) <= 2:
        return solution

    new_sol = {
        "teams": solution["teams"],
        "schedule": deep_copy_schedule(solution["schedule"]),
        "start": solution["start"].copy(),
        "end": solution["end"].copy(),
    }

    valid = list(range(1, len(new_sol["schedule"][day])))

    src = random.choice(valid)
    dst = random.choice(valid)

    if src == dst or not new_sol["schedule"][day][src]:
        return solution

    idx = random.randrange(len(new_sol["schedule"][day][src]))
    I = new_sol["schedule"][day][src].pop(idx)

    pos = random.randrange(len(new_sol["schedule"][day][dst]) + 1)
    new_sol["schedule"][day][dst].insert(pos, I)

    if not recompute_times_for_day_safe(new_sol, day, data):
        return solution

    if is_same_day(solution, new_sol, day):
        return solution

    return new_sol


# =================================================================
# MOVE 4 : déplacer une intervention vers un autre jour
# =================================================================
def move_change_day(solution, data, return_days=False):
    max_day = data["max_day"]

    old_day = random.randint(0, max_day)
    new_day = random.randint(0, max_day)

    if old_day == new_day:
        return (solution, old_day, new_day) if return_days else solution

    sched = solution["schedule"]

    if not sched[old_day]:
        return (solution, old_day, new_day) if return_days else solution

    new_sol = {
        "teams": solution["teams"],
        "schedule": deep_copy_schedule(solution["schedule"]),
        "start": solution["start"].copy(),
        "end": solution["end"].copy(),
    }

    # trouver une équipe source ≠ 0
    valid_old = list(range(1, len(new_sol["schedule"][old_day])))
    if not valid_old:
        return (solution, old_day, new_day) if return_days else solution

    team_old = random.choice(valid_old)

    if not new_sol["schedule"][old_day][team_old]:
        return (solution, old_day, new_day) if return_days else solution

    idx = random.randrange(len(new_sol["schedule"][old_day][team_old]))
    I = new_sol["schedule"][old_day][team_old].pop(idx)

    # équipe de destination
    valid_new = list(range(1, len(new_sol["schedule"][new_day])))
    if not valid_new:
        return (solution, old_day, new_day) if return_days else solution

    team_new = random.choice(valid_new)
    pos = random.randrange(len(new_sol["schedule"][new_day][team_new]) + 1)
    new_sol["schedule"][new_day][team_new].insert(pos, I)

    # recalcul local
    if not recompute_times_for_day_safe(new_sol, old_day, data):
        return (solution, old_day, new_day) if return_days else solution

    if not recompute_times_for_day_safe(new_sol, new_day, data):
        return (solution, old_day, new_day) if return_days else solution

    # éviter les moves nuls
    if is_same_day(solution, new_sol, old_day) and is_same_day(solution, new_sol, new_day):
        return (solution, old_day, new_day) if return_days else solution

    if return_days:
        return new_sol, old_day, new_day
    return new_sol
