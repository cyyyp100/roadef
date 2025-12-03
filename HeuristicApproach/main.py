from pathlib import Path

from parser import load_ft2007_instance
from data_structures import create_empty_solution
from simulated_annealing import simulated_annealing
from evaluation import compute_cost
from export import export_solution_ft


def main(set_name="Instances_set_A", data_id="Data1"):
    """
    Exécute une instance complète FT2007 :
        - parse
        - solution initiale
        - SA
        - export
    """

    # Dossier contenant Instance.txt / Interv_list.txt / Tech_list.txt
    folder = Path("Data") / set_name / data_id

    print("Chargement instance FT2007 depuis :", folder)

    # 1) Parser FT2007
    data = load_ft2007_instance(folder)

    print("\n=== Données chargées ===")
    print(f"Instance : {data['instance_name']}")
    print(f"Interventions : {data['n_interv']}")
    print(f"Techniciens   : {data['n_tech']}")
    print(f"Domaines      : {data['domains']}")
    print(f"Niveaux       : {data['levels']}")
    print(f"Max day       : {data['max_day']}")
    print("---------------------------")

    # 2) Solution initiale
    sol0 = create_empty_solution(data)
    cost0 = compute_cost(sol0, data)
    print(f"Coût initial : {cost0}")

    # 3) Recuit simulé FT2007
    final = simulated_annealing(
        sol0,
        data,
        T0=3000,
        alpha=0.995,
        iter_max=50000
    )

    cost_f = compute_cost(final, data)
    print("\n===========================")
    print(" SOLUTION FINALE FT2007")
    print("===========================")
    print(f"Coût final   : {cost_f}")
    print(f"Amélioration : {cost0 - cost_f}")

    # 4) Export solution FT2007
    export_folder = Path("Solutions") / set_name / data_id
    export_folder.mkdir(parents=True, exist_ok=True)
    export_solution_ft(final, data, export_folder)

    print("\nSolution exportée dans :", export_folder)


if __name__ == "__main__":
    main("Instances_set_B", "Data3")
