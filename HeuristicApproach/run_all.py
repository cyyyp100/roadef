from pathlib import Path
from main import main   # ta fonction main(set_name, folder_name)


def run_set(set_name):
    """
    Exécute toutes les instances d’un set donné :
    Instances_set_A, Instances_set_B, Instances_set_X
    """
    base = Path("data") / set_name

    if not base.exists():
        print(f"⚠ Le set {set_name} n’existe pas dans data/")
        return

    folders = sorted([p.name for p in base.iterdir() if p.is_dir() and p.name.startswith("data")])

    if not folders:
        print(f"⚠ Aucun dossier 'dataX' trouvé dans {set_name}")
        return

    print(f"\n====================================")
    print(f" TRAITEMENT DU SET : {set_name}")
    print(f"====================================\n")

    for folder in folders:
        print(f"\n⇒ Instance : {set_name}/{folder}")
        main(set_name, folder)


def run_all():
    """
    Traite les 3 sets : A, B, X
    """
    for set_name in ["Instances_set_A", "Instances_set_B", "Instances_set_X"]:
        run_set(set_name)


if __name__ == "__main__":
    run_all()
