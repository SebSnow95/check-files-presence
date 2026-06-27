# check_files.py — Spécification et guide d'utilisation

## 1. Objectif

`check_files.py` est un script Python qui compare le contenu de deux répertoires :

- **Répertoire A (source)** : le répertoire de référence contenant les fichiers à vérifier.
- **Répertoire B (destination)** : le répertoire dans lequel on cherche à confirmer la présence de ces fichiers.

Le script identifie les fichiers présents dans A mais absents dans B, propose de les copier, et produit un rapport écrit.

---

## 2. Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| Analyse en temps réel | Chaque fichier analysé s'affiche dans le terminal au fur et à mesure |
| Classement par taille | Les fichiers absents sont séparés en deux groupes : < 100 Ko et > 100 Ko |
| Chemin source | Le chemin absolu de chaque fichier manquant est affiché |
| Copie optionnelle | Après l'analyse, le script propose de copier les fichiers manquants vers B |
| Rapport .txt | Un fichier `rapport_verification.txt` est généré avec l'intégralité des résultats |

---

## 3. Prérequis

- Python 3.10 ou supérieur
- Aucune librairie externe requise (uniquement la bibliothèque standard Python)

---

## 4. Lancement du script

```bash
python check_files.py
```

Le script pose deux questions :

```
=== Vérification de présence de fichiers ===

Répertoire A (source) : /Volumes/Lexar/Bd-Revues/From-IPad 
Répertoire B (cible)  : /Volumes/Mac/Bd-Revues
```

> **Important** : si le nom d'un répertoire contient un espace en fin de nom
> (ex : `From-IPad `), saisir l'espace avant d'appuyer sur Entrée.
> Le script préserve les espaces internes aux chemins.

---

## 5. Déroulement type

### Étape 1 — Analyse

```
──────────────────────────────────────────────────
Analyse en cours...

  Analyse : album1.cbz
  Analyse : album2.cbz
  Analyse : album3.cbz
```

### Étape 2 — Rapport affiché dans le terminal

```
Répertoire A : /Volumes/Lexar/Bd-Revues/From-IPad 
Répertoire B : /Volumes/Mac/Bd-Revues

──────────────────────────────────────────────────
Fichiers analysés : 3
Présents dans B   : 1
Absents dans B    : 2
──────────────────────────────────────────────────

[PRESENT] (1 fichier(s))
  ✓  album1.cbz

[ABSENT] (2 fichier(s))

  > 100 Ko (2 fichier(s))
  ✗  album2.cbz  (45.3 Mo)
       Source : /Volumes/Lexar/Bd-Revues/From-IPad /album2.cbz
  ✗  album3.cbz  (128.7 Mo)
       Source : /Volumes/Lexar/Bd-Revues/From-IPad /album3.cbz
```

### Étape 3 — Proposition de copie

```
──────────────────────────────────────────────────
2 fichier(s) manquant(s). Copier vers la destination ? (o/n) : o

  [1/2] Copie : album2.cbz ... OK
  [2/2] Copie : album3.cbz ... OK

Copie terminée : 2 réussi(s), 0 erreur(s).
```

Répondre `n` annule la copie sans modifier les fichiers.

### Étape 4 — Sauvegarde du rapport

```
Rapport sauvegardé : /chemin/vers/rapport_verification.txt
```

Le fichier est créé dans le répertoire depuis lequel le script est lancé.

---

## 6. Fichier rapport_verification.txt

Le rapport contient :

- La date et l'heure de l'analyse
- Les chemins absolus des deux répertoires
- Le résumé chiffré (total analysé, présents, absents)
- La liste des fichiers présents (✓)
- La liste des fichiers absents (✗) avec taille et chemin source, classés par taille
- Si une copie a été effectuée : le résultat fichier par fichier (succès ou erreur)

---

## 7. Limites et comportements à connaître

| Comportement | Détail |
|---|---|
| Comparaison par nom | Deux fichiers de même nom mais de contenu différent seront considérés comme présents |
| Fichiers uniquement | Les sous-répertoires sont ignorés (pas d'analyse récursive) |
| Seuil de taille | Le seuil de séparation est fixé à 100 000 octets (environ 97 Ko) |
| Écrasement | La copie ne vérifie pas si un fichier existe déjà dans B avant d'écraser |
| Rapport | Le fichier `rapport_verification.txt` est écrasé à chaque exécution |

---

## 8. Structure du code

```
check_files.py
│
├── _format_size(size_bytes)
│     Convertit des octets en chaîne lisible (Ko, Mo, Go, To)
│
├── _print_absent(lines, absent)
│     Classe et formate les fichiers absents en deux groupes (< / > 100 Ko)
│
├── copy_missing_files(absent, path_b)
│     Copie les fichiers manquants vers path_b, affiche la progression,
│     retourne les lignes de résultat pour le rapport
│
└── check_files_presence(dir_a, dir_b)
      Fonction principale : validation, analyse, affichage, copie, rapport
```
