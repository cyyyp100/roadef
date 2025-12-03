# ============================================
#  export_ft2007.py
#  Export officiel ROADEF FT2007 :
#     - Interv_list
#     - Team_list
# ============================================

from pathlib import Path

HMAX = 120


def export_interv_list(solution, data, folder: Path):
    """
    Écrit le fichier Interv_list au format officiel ROADEF FT2007 :
    
        <interv_id> <day> <start> <team_id>

    - Les interventions non planifiées sont ignorées
    - Les interventions placées dans team 0 (absents) => ignorées
    """

    path = folder / "Interv_list"

    # cherche dans quelle équipe chaque intervention est
    team_of_I = {}

    for day, teams in solution["schedule"].items():
        for team_id, interv_list in enumerate(teams):
            if team_id == 0:
                continue  # absents → non valide
            for I in interv_list:
                team_of_I[I] = (day, team_id)

    start = solution["start"]

    rows = []
    for I in sorted(data["interventions"].keys()):
        if I not in start:
            # intervention non planifiée → ignorée (checker compte comme abandonnée)
            continue

        if I not in team_of_I:
            # équipe absente → impossibilité
            continue

        (day, team_id) = team_of_I[I]
        rows.append(f"{I} {day} {start[I]} {team_id}")

    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def export_team_list(solution, data, folder: Path):
    """
    Écrit le fichier Team_list au format officiel :
    
        <day> <team_id> t1 t2 t3 ...

    - On ignore l’équipe 0 (absents)
    """

    path = folder / "Team_list"

    rows = []

    for day in range(data["max_day"] + 1):
        teams = solution["teams"][day]

        for team_id, team in enumerate(teams):
            if team_id == 0:
                continue  # absents non exportés

            # ligne du type :
            #   3 1  5 7 8
            tech_str = " ".join(str(t) for t in team)
            rows.append(f"{day} {team_id} {tech_str}")

    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def export_solution_ft(solution, data, folder: Path):
    """
    Fonction unique appelée par main.py :
    écrit Interv_list + Team_list dans le dossier fourni.
    """

    folder.mkdir(parents=True, exist_ok=True)

    export_interv_list(solution, data, folder)
    export_team_list(solution, data, folder)

    print("→ Fichiers FT2007 générés :")
    print("   -", folder / "Interv_list")
    print("   -", folder / "Team_list")
