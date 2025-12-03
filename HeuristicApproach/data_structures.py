# ============================================
#  data_structures.py — ROADEF 2007
#  Construction d'une solution initiale simple
# ============================================

def create_empty_solution(data):
    """
    Produit une solution initiale TRÈS simple :
      - 1 équipe par technicien
      - on assigne les interventions dans l'ordre de leurs prédécesseurs
      - chaque intervention est placée au plus tôt
      - start/end sont recalculés proprement

    Retourne :
        solution = {
            "teams": { day : [ [tech1], [tech2], ... ] },
            "schedule": { day : [ [i1,i2], [i3], ... ] },
            "start": {i: t},
            "end": {i: t2}
        }
    """

    max_day = data["max_day"]
    n_tech = data["n_tech"]

    # ==========================================================
    # Construire les équipes (1 technicien = 1 équipe)
    # ==========================================================
    teams = {}
    schedule = {}
    for day in range(max_day + 1):
        teams[day] = [[t] for t in range(1, n_tech + 1)]
        schedule[day] = [[] for _ in range(n_tech)]

    start = {}
    end = {}

    # ==========================================================
    # Ordonner les interventions par prédécesseurs
    # ==========================================================
    interventions = data["interventions"]
    durations = data["duration"]
    pred = data["pred"]

    # tri topologique simplifié
    ordered = sorted(interventions.keys(), key=lambda i: len(pred[i]))

    # ==========================================================
    # Placement des interventions au plus tôt
    # ==========================================================
    for I in ordered:
        duration = durations[I]

        # earliest = fin max des prédécesseurs
        earliest = 0
        if pred[I]:
            earliest = max(end.get(p, 0) for p in pred[I])

        # on tente tous les jours depuis earliest/H jusqu'à max_day
        placed = False

        day0 = earliest // 120

        for day in range(day0, max_day + 1):
            for team_id in range(len(schedule[day])):
                if schedule[day][team_id]:
                    last = schedule[day][team_id][-1]
                    available_time = end[last]
                else:
                    available_time = day * 120

                st = max(available_time, earliest)
                en = st + duration

                start[I] = st
                end[I] = en

                schedule[day][team_id].append(I)
                placed = True
                break

            if placed:
                break

        if not placed:
            # fallback : dernière équipe du dernier jour
            day = max_day
            team_id = 0
            if schedule[day][team_id]:
                last = schedule[day][team_id][-1]
                st = end[last]
            else:
                st = day * 120
            en = st + duration

            start[I] = st
            end[I] = en
            schedule[day][team_id].append(I)

    # ==========================================================
    # Retour solution
    # ==========================================================
    return {
        "teams": teams,
        "schedule": schedule,
        "start": start,
        "end": end,
    }
