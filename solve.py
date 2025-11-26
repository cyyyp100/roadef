from __future__ import annotations

from pathlib import Path

from roadef_solver.cli import main as solver_main


# Dossier de base = dossier du projet (là où se trouve solve.py)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "sorties"

# ⚠ Mets ici exactement les noms de tes dossiers dans data/
# (toi tu utilises visiblement "Instances_set_A", "Instances_set_B", "Instances_set_X")
INSTANCE_SETS = ["Instances_set_A", "Instances_set_B", "Instances_set_X"]

# data1..data10
NB_DATA = 10


def run_one(instance_set: str, data_index: int) -> int:
    """
    Lance le solver sur une instance donnée, par ex :
    Instances_set_A / data3.
    """
    data_name = f"data{data_index}"  # data1, data2, ...
    input_dir = DATA_DIR / instance_set / data_name
    output_dir = OUTPUT_DIR / instance_set / data_name

    # Fichiers d'entrée attendus dans input_dir
    instance_path = input_dir / "instance"
    interventions_path = input_dir / "interv_list"
    technicians_path = input_dir / "tech_list"

    if not input_dir.is_dir():
        print(f"[WARN] Dossier introuvable : {input_dir}")
        return 1
    for path in (instance_path, interventions_path, technicians_path):
        if not path.is_file():
            print(f"[WARN] Fichier manquant : {path}")
            return 1

    # On crée le dossier de sortie s'il n'existe pas
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Résolution de {instance_set}/{data_name} ===")
    print(f"Input  : {input_dir}")
    print(f"Output : {output_dir}")

    # ⚠ Ici on respecte **exactement** la signature du CLI :
    # solve.py instance interventions technicians --output OUTPUT_DIR
    argv = [
        str(instance_path),
        str(interventions_path),
        str(technicians_path),
        "--output",
        str(output_dir),
        # Tu peux personnaliser ici si tu veux :
        # "--hmax", "120",
        # "--max-days", "365",
    ]

    try:
        code = solver_main(argv)
    except SystemExit as e:
        # main() appelle sys.exit(), on récupère le code
        code = int(e.code)

    print(f"→ Terminé avec code {code}")
    return code


def run_all() -> int:
    """
    Lance toutes les instances pour tous les jeux d'instances.
    """
    global_status = 0

    for instance_set in INSTANCE_SETS:
        print("\n############################")
        print(f"### Jeu : {instance_set}")
        print("############################")

        for k in range(1, NB_DATA + 1):
            code = run_one(instance_set, k)
            if code != 0 and global_status == 0:
                global_status = code

    if global_status == 0:
        print("\n✅ Toutes les instances se sont terminées sans erreur.")
    else:
        print("\n⚠️ Au moins une instance a échoué. Regarde les messages ci-dessus.")

    return global_status


if __name__ == "__main__":
    raise SystemExit(run_all())