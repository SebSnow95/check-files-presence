"""
check_files.py
--------------
Vérifie si les fichiers présents dans un répertoire source (A) sont aussi
présents dans un répertoire de destination (B). Affiche l'avancement en
temps réel, classe les fichiers manquants par taille, propose de les copier
et sauvegarde un rapport complet dans un fichier .txt.
"""

import shutil
import sys
from pathlib import Path
from datetime import datetime


def _format_size(size_bytes: int) -> str:
    """Convertit un nombre d'octets en chaîne lisible (Ko, Mo, Go...)."""
    for unit in ("o", "Ko", "Mo", "Go"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} To"


def _print_absent(lines: list, absent: list) -> None:
    """
    Ajoute dans `lines` les fichiers absents répartis en deux groupes :
      - fichiers < 100 Ko (souvent des miniatures ou métadonnées)
      - fichiers >= 100 Ko (contenu principal)
    Chaque entrée inclut le nom, la taille et le chemin source complet.
    """
    # Séparation selon le seuil de 100 Ko (100 000 octets)
    small = [f for f in absent if f.stat().st_size < 100_000]
    large = [f for f in absent if f.stat().st_size >= 100_000]

    if small:
        lines.append(f"\n  < 100 Ko ({len(small)} fichier(s))")
        for f in small:
            size = _format_size(f.stat().st_size)
            lines.append(f"  ✗  {f.name}  ({size})")
            lines.append(f"       Source : {f.resolve()}")

    if large:
        lines.append(f"\n  > 100 Ko ({len(large)} fichier(s))")
        for f in large:
            size = _format_size(f.stat().st_size)
            lines.append(f"  ✗  {f.name}  ({size})")
            lines.append(f"       Source : {f.resolve()}")


def copy_missing_files(absent: list, path_b: Path) -> list[str]:
    """
    Copie chaque fichier de `absent` vers `path_b`.
    Affiche la progression fichier par fichier dans le terminal.
    Retourne les lignes à ajouter au rapport (succès et erreurs).
    shutil.copy2 préserve les métadonnées (dates, permissions).
    """
    copy_lines = []
    copy_lines.append(f"\n{'─' * 50}")
    copy_lines.append("Copie des fichiers manquants...\n")
    errors = []

    for i, f in enumerate(absent, 1):
        dest = path_b / f.name
        # flush=True force l'affichage immédiat sans attendre le saut de ligne
        print(f"  [{i}/{len(absent)}] Copie : {f.name} ...", end=" ", flush=True)
        try:
            shutil.copy2(f, dest)
            print("OK")
            copy_lines.append(f"  ✓  {f.name}  →  {dest}")
        except Exception as e:
            print(f"ERREUR ({e})")
            errors.append(f.name)
            copy_lines.append(f"  ✗  {f.name}  →  ERREUR : {e}")

    copy_lines.append(f"\nCopie terminée : {len(absent) - len(errors)} réussi(s), {len(errors)} erreur(s).")
    return copy_lines


def check_files_presence(dir_a: str, dir_b: str) -> None:
    """
    Fonction principale :
      1. Valide l'existence des deux répertoires.
      2. Analyse chaque fichier de A et vérifie sa présence dans B par nom.
      3. Construit et affiche le rapport (présents / absents avec taille).
      4. Propose de copier les fichiers manquants vers B.
      5. Sauvegarde le rapport complet dans rapport_verification.txt.

    La comparaison se fait sur le nom du fichier uniquement, pas sur le contenu.
    Les sous-répertoires sont ignorés.
    """
    path_a = Path(dir_a)
    path_b = Path(dir_b)

    # Vérification de l'existence des répertoires avant tout traitement
    if not path_a.is_dir():
        print(f"Erreur : le répertoire A '{dir_a}' n'existe pas.")
        sys.exit(1)
    if not path_b.is_dir():
        print(f"Erreur : le répertoire B '{dir_b}' n'existe pas.")
        sys.exit(1)

    # Récupération des fichiers uniquement (les sous-dossiers sont exclus)
    files_a = sorted(f for f in path_a.iterdir() if f.is_file())

    if not files_a:
        print(f"Aucun fichier trouvé dans '{dir_a}'.")
        return

    present = []  # fichiers de A trouvés dans B
    absent = []   # fichiers de A absents de B

    print(f"\n{'─' * 50}")
    print("Analyse en cours...\n")

    # Parcours fichier par fichier avec affichage en temps réel
    for file in files_a:
        print(f"  Analyse : {file.name}")
        if (path_b / file.name).is_file():
            present.append(file)
        else:
            absent.append(file)

    total = len(files_a)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construction du rapport sous forme de liste de lignes
    lines = []
    lines.append("=== Rapport de vérification de fichiers ===")
    lines.append(f"Date : {timestamp}")
    lines.append(f"Répertoire A : {path_a.resolve()}")
    lines.append(f"Répertoire B : {path_b.resolve()}")
    lines.append(f"\n{'─' * 50}")
    lines.append(f"Fichiers analysés : {total}")
    lines.append(f"Présents dans B   : {len(present)}")
    lines.append(f"Absents dans B    : {len(absent)}")
    lines.append(f"{'─' * 50}")

    if present:
        lines.append(f"\n[PRESENT] ({len(present)} fichier(s))")
        for f in present:
            lines.append(f"  ✓  {f.name}")

    if absent:
        lines.append(f"\n[ABSENT] ({len(absent)} fichier(s))")
        _print_absent(lines, absent)

    # Affichage du rapport dans le terminal (à partir de "Répertoire A")
    print(f"\n{'─' * 50}")
    print("\n".join(lines[lines.index(next(l for l in lines if l.startswith("Répertoire A"))):]))

    # Proposition de copie uniquement s'il y a des fichiers manquants
    if absent:
        print(f"\n{'─' * 50}")
        reponse = input(f"\n{len(absent)} fichier(s) manquant(s). Copier vers la destination ? (o/n) : ").strip().lower()
        if reponse == "o":
            copy_lines = copy_missing_files(absent, path_b)
            lines.extend(copy_lines)  # ajout du résultat de copie au rapport
        else:
            print("Copie annulée.")

    # Sauvegarde du rapport dans le répertoire de travail courant
    report_path = Path("rapport_verification.txt")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRapport sauvegardé : {report_path.resolve()}")


if __name__ == "__main__":
    print("=== Vérification de présence de fichiers ===\n")
    # strip("\n\r") préserve les espaces dans le chemin (ex: "From-IPad ")
    dir_a = input("Répertoire A (source) : ").strip("\n\r")
    dir_b = input("Répertoire B (cible)  : ").strip("\n\r")
    check_files_presence(dir_a, dir_b)
