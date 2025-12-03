# ===========================================================
#  constraints.py — ROADEF 2007 compatible parser FT2007
# ===========================================================

def respects_precedence(solution, data):
    """Check global des prédécesseurs."""
    start = solution["start"]
    end = solution["end"]
    pred = data["pred"]

    for I, preds in pred.items():
        for P in preds:
            if end.get(P, 0) > start.get(I, 0):
                return False
    return True


def no_overlap_day(solution, day):
    """Vérifie qu’une équipe n’a pas de chevauchement sur un seul jour."""
    start = solution["start"]
    end = solution["end"]
    teams = solution["schedule"][day]

    for interv_list in teams:
        for i in range(len(interv_list) - 1):
            I = interv_list[i]
            J = interv_list[i+1]
            if end[I] > start[J]:
                return False
    return True


def team_has_skills(team, intervention, data):
    """
    Vérifie que l’équipe couvre les compétences requises.
    Format FT2007 :
        skills[tech] = [d1, d2, d3, d4]
        requirements = matrix [domain][level]
    """
    req = data["interventions"][intervention]["requirements"]
    tech_skills = data["skills"]

    team_cap = [0] * data["domains"]
    for tech in team:
        sk = tech_skills[tech]
        for d in range(data["domains"]):
            team_cap[d] = max(team_cap[d], sk[d])

    for d in range(data["domains"]):
        needed = max(req[d])
        if needed > 0 and team_cap[d] < needed:
            return False
    return True


def tech_available(tech, day, start, end, data):
    """Vérifie que le tech n'est pas indisponible ce jour-là."""
    return day not in data["unavailability"][tech]


def team_available(team, day, start, end, data):
    """Chaque tech de l’équipe doit être dispo."""
    for tech in team:
        if not tech_available(tech, day, start, end, data):
            return False
    return True


def within_time_window(intervention, start, end, data):
    return True


# ===========================================================
#   VERSION CORRIGÉE : respecte changed_days
# ===========================================================
def respects_all_constraints(solution, data, changed_days=None):
    """Check localisé : prédécesseurs, overlap, skills, dispo."""

    # 1) Prédécesseurs (global)
    if not respects_precedence(solution, data):
        return False

    # 2) Si aucun jour précisé → on check tout (initial SA, export…)
    if changed_days is None:
        changed_days = list(solution["schedule"].keys())

    # 3) Overlap sur les seuls jours concernés
    for day in changed_days:
        if not no_overlap_day(solution, day):
            return False

    # 4) Check skills & availability (sur changed_days uniquement)
    for day in changed_days:
        teams = solution["teams"][day]
        interv_lists = solution["schedule"][day]

        for k, team in enumerate(teams):
            for I in interv_lists[k]:
                st = solution["start"][I]
                en = solution["end"][I]

                if not team_has_skills(team, I, data):
                    return False
                if not team_available(team, day, st, en, data):
                    return False
                if not within_time_window(I, st, en, data):
                    return False

    return True
