import random

from moves import (
    move_reorder,
    move_swap_between_teams,
    move_shift,
    move_change_day,
)

from constraints import respects_all_constraints


# ================================================================
# Liste des mouvements autorisés
# ================================================================
MOVE_FUNCS = [
    move_reorder,
    move_swap_between_teams,
    move_shift,
    move_change_day,   # signature spéciale : pas de jour
]


# ================================================================
#  GENERATION D'UN VOISIN VALIDE (corrigé avec changed_days)
# ================================================================
def generate_neighbor(solution, data, max_tries=200):
    """
    Génère un voisin valide.
    Le SA n'appelle plus jamais des contraintes globales.
    On vérifie seulement les jours modifiés.
    """

    max_day = data["max_day"]

    for _ in range(max_tries):

        move = random.choice(MOVE_FUNCS)

        # =============================================================
        #  Cas spécial : move_change_day (pas de paramètre 'day')
        # =============================================================
        if move is move_change_day:
            try:
                new_sol, old_day, new_day = move(solution, data, return_days=True)
            except Exception:
                continue

            changed_days = [old_day, new_day]

        # =============================================================
        #  Cas standard : moves dépendant du jour
        # =============================================================
        else:
            day = random.randint(0, max_day)
            try:
                new_sol = move(solution, day, data)
            except Exception:
                continue

            changed_days = [day]

        # =============================================================
        #  Check validité locale des contraintes
        # =============================================================
        try:
            if respects_all_constraints(new_sol, data, changed_days=changed_days):
                # Debug : confirmer que le move passe
                # print("Move accepté :", move.__name__, "jours modifiés :", changed_days)
                return new_sol
        except Exception:
            continue

        # Debug : move invalide
        #print("VALID MOVE:", move.__name__, "changed days:", changed_days)

        # Debug éventuel
        # print("Trying move:", move.__name__)

    # =============================================================
    # Si rien trouvé : retourner solution identique
    # (le SA gère ce cas)
    # =============================================================
    return solution
