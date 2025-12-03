# ============================================
#  evaluation.py — Cost function ROADEF 2007 (compatible Set B)
# ============================================

HMAX = 120

def compute_cost(solution, data):
    """
    Score officiel FT2007 compatible avec les datasets Set A / Set B.
    Certains fichiers n'ont pas les champs "synchronization" ni "abandon_cost",
    donc ils sont traités par défaut.
    """

    start = solution["start"]
    end = solution["end"]
    interventions = data["interventions"]
    
    # poids par composante
    Wq = data.get("Wq", 1)
    Ws = data.get("Ws", 0)        # pas de sync dans Set B → 0
    Wu = data.get("Wu", 10000)
    Wl = data.get("Wl", 1)

    Q = 0
    S = 0
    U = 0
    L = 0

    # pondération des priorités
    weight_prio = {1: 28, 2: 14, 3: 4, 4: 1}

    # -----------------------------------------
    # 1) Q = completion time × priority weight
    # -----------------------------------------
    for I, info in interventions.items():
        prio = info["priority"]
        w = weight_prio[prio]

        if I in end:
            Q += w * end[I]
        else:
            # fallback si abandon_cost non présent
            abandon_c = info.get("abandon_cost", 100000)
            Q += abandon_c

    # -----------------------------------------
    # 2) U = penalties for tech unavailability
    # -----------------------------------------
    for day, teams in solution["teams"].items():
        for k, team in enumerate(teams):
            for I in solution["schedule"][day][k]:
                st = start[I]
                en = end[I]
                for tech in team:
                    if day in data["unavailability"][tech]:
                        U += 1  # pénalité par violation (simplifiée)

    # -----------------------------------------
    # 3) S = synchronization penalties (optional)
    # -----------------------------------------
    for I, info in interventions.items():
        if "synchronization" not in info:
            continue  # Set B → ignore

        group = info["synchronization"]
        if not group:
            continue

        times = [end[J] for J in group if J in end]
        if len(times) > 1:
            S += max(times) - min(times)

    # -----------------------------------------
    # 4) L = length of schedule (last day used)
    # -----------------------------------------
    if end:
        L = max(end.values()) // HMAX

    # -----------------------------------------
    # TOTAL COST
    # -----------------------------------------
    return Wq * Q + Ws * S + Wu * U + Wl * L
