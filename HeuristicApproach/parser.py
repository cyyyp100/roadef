# ============================================
#  parser.py — ROADEF 2007 (format ENAC)
# ============================================

from pathlib import Path


# ==========================================================
#               PARSE INSTANCE.TXT
# ==========================================================

def parse_instance_file(path: Path):
    """
    Format :
    name domains level techs interv abandon
    example:
        test4 4 3 7 20 0
    """

    lines = [l.strip() for l in path.read_text().splitlines() if l.strip()]

    if not lines[0].lower().startswith("name"):
        raise ValueError("Première ligne doit commencer par 'name'")

    tokens = lines[1].split()
    if len(tokens) != 6:
        raise ValueError("Ligne instance doit contenir 6 champs")

    name, domains, levels, techs, interv, abandon = tokens

    return {
        "instance_name": name,
        "domains": int(domains),
        "levels": int(levels),
        "n_tech": int(techs),
        "n_interv": int(interv),
        "abandon_cost_default": int(abandon),
    }


# ==========================================================
#               PARSE INTERV_LIST.TXT
# ==========================================================

def parse_interventions_file(path: Path, domains, levels):
    """
    Format :
    number time [ preds ] prio cost  d1_1 d1_2 d1_3  d2_1 ...
    Exemple :
        1 60 [ ] 1 300 1 0 0 0 0 0 4 3 0 0 0 0
    """

    interv = {}

    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or not line[0].isdigit():
            continue

        tokens = line.split()

        id_ = int(tokens[0])
        time = int(tokens[1])

        # prédécesseurs entre crochets
        preds_raw = line[line.index("[")+1 : line.index("]")]
        preds = [int(x) for x in preds_raw.split() ] if preds_raw.strip() else []

        # après les crochets
        rest = line[line.index("]")+1:].strip().split()

        prio = int(rest[0])
        abandon = int(rest[1])

        # matrice domaines × niveaux = domains*levels valeurs
        req_raw = rest[2:]
        if len(req_raw) != domains * levels:
            raise ValueError("Nombre incorrect de niveaux de compétence")

        # reconstruction matrice NxM
        req = []
        idx = 0
        for d in range(domains):
            row = []
            for l in range(levels):
                row.append(int(req_raw[idx]))
                idx += 1
            req.append(row)

        interv[id_] = {
            "duration": time,
            "pred": preds,
            "priority": prio,
            "abandon_cost": abandon,
            "requirements": req,
        }

    return interv


# ==========================================================
#               PARSE TECH_LIST.TXT
# ==========================================================

def parse_techs_file(path: Path, domains):
    """
    Format :
    tech d1 d2 d3 d4 dispo
    Exemple :
        1 3 1 1 3 [ 1 ]
    """

    techs = {}
    unavailability = {}

    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or not line[0].isdigit():
            continue

        parts = line.split()

        id_ = int(parts[0])

        # compétences
        skills = [int(x) for x in parts[1:1+domains]]

        # indisponibilités : dans les crochets
        brack = line[line.index("[")+1 : line.index("]")]
        if brack.strip():
            days = [int(x) for x in brack.split()]
        else:
            days = []

        techs[id_] = skills
        unavailability[id_] = days

    return techs, unavailability


# ==========================================================
#       FONCTION PRINCIPALE DE CHARGEMENT
# ==========================================================

def load_ft2007_instance(folder: Path):
    """
    Lit :
        - Instance
        - Interv_list
        - Tech_list
    et retourne un dictionnaire 'data'
    """

    inst_file = folder / "Instance"
    interv_file = folder / "Interv_list"
    tech_file = folder / "Tech_list"

    print("Chargement des fichiers :")
    print(" -", inst_file)
    print(" -", interv_file)
    print(" -", tech_file)

    meta = parse_instance_file(inst_file)

    interventions = parse_interventions_file(
        interv_file,
        meta["domains"],
        meta["levels"],
    )

    tech_skills, unavailability = parse_techs_file(
        tech_file,
        meta["domains"],
    )

    # construit structure finale data
    data = {
        **meta,
        "interventions": interventions,
        "skills": tech_skills,
        "unavailability": unavailability,

        # valeurs dérivées
        "duration": {i: interventions[i]["duration"] for i in interventions},
        "pred": {i: interventions[i]["pred"] for i in interventions},

        # jours max = approx horizon (max possible time // 120)
        "max_day": max((interventions[i]["duration"] for i in interventions)) + 10
    }

    return data
