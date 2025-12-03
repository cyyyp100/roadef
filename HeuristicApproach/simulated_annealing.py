import math
import random
from evaluation import compute_cost
from neighbor import generate_neighbor


def simulated_annealing(
    solution,
    data,
    T0=5000,
    alpha=0.9993,
    iter_max=20000,
    stall_max=3000
):
    """
    SA simple mais optimisé :
    - refroidissement lent (important pour FT2007)
    - acceptation probabiliste
    - redémarrage partiel si stagnation
    """

    current = solution
    best = solution
    current_cost = compute_cost(current, data)
    best_cost = current_cost
    T = T0

    stall = 0  # compteur de stagnation

    for it in range(iter_max):

        # --- VOISINAGE ---
        neighbor = generate_neighbor(current, data)

        cost_neighbor = compute_cost(neighbor, data)
        delta = cost_neighbor - current_cost

        # --- ACCEPTATION ---
        if delta < 0:
            accept = True
        else:
            prob = math.exp(-delta / max(T, 1e-9))
            accept = random.random() < prob

        if accept:
            current = neighbor
            current_cost = cost_neighbor

            # nouveau meilleur ?
            if current_cost < best_cost:
                best = current
                best_cost = current_cost
                stall = 0
            else:
                stall += 1
        else:
            stall += 1

        # --- REFROIDISSEMENT ---
        T *= alpha

        # --- ANTI-STAGNATION ---
        if stall > stall_max:
            # petit reheat pour éviter de rester bloqué
            T = T0 * 0.3
            stall = 0

        # print every 5000 iter (debug)
        if it % 5000 == 0:
            print(f"[DEBUG] iter={it}, best={best_cost}")

    return best
