# Cahier des charges — Outil Excel de Reporting Hebdomadaire de Projets

## 1. Contexte et objectifs

Aujourd'hui, le reporting hebdomadaire (scopes EUS, M&A, …) est produit dans un classeur où chaque section est une cellule fusionnée dans laquelle les mises à jour datées ("Update 08/06", "Update 15/06", …) sont empilées manuellement au fil des semaines.

**Limites constatées sur le modèle actuel :**
- L'historique est illisible par la machine : impossible de trier, filtrer, ou de savoir automatiquement ce qui a changé depuis la semaine précédente sans surlignage manuel.
- Risque d'écrasement/perte de contenu en copiant-collant la structure d'une semaine à l'autre.
- Duplication de la mise en forme entre les scopes (EUS, M&A, …), donc double saisie et risque de divergence du gabarit.
- Aucune vision consolidée (KPI, nombre de risques critiques, projets en retard) sans relecture manuelle intégrale.

**Objectif de l'outil :** séparer la **donnée** (projets, incidents, décisions, risques, opportunités, besoins, finance) de sa **restitution** (le document hebdomadaire mis en forme), afin de :
- fiabiliser la saisie et l'historisation,
- générer automatiquement la mise en page du rapport par scope,
- mettre en évidence automatiquement les nouveautés de la semaine,
- fournir un tableau de bord transverse.

## 2. Périmètre fonctionnel

L'outil couvre les 6 sections identifiées dans le gabarit actuel, pour un nombre quelconque de scopes (EUS, M&A, et tout scope futur) :

1. Weekly Progress → **Projets** (Achieved Objectives, Completed Tasks, Next Steps)
2. Major Events → **Incidents critiques** et **Décisions stratégiques**
3. Risks and Opportunities → **Risques** (Probabilité, Impact, Plan de mitigation) et **Opportunités**
4. Needs and Support → **Besoins / Support requis**
5. Finance → **Bcase, Book FM, Sourcing**
6. Other Information → **Éléments libres** propres à chaque scope

## 3. Modèle de données

Principe : chaque section ci-dessus partage la même forme (un identifiant, un titre, un statut, un ou deux champs descriptifs fixes, un propriétaire, et un **journal de mises à jour datées**). Le modèle retient donc **deux tables pivots** plutôt qu'une table par section, afin d'éviter la duplication de structure :

### 3.1 Table `T_Elements` (un enregistrement = un projet / incident / décision / risque / opportunité / besoin / ligne finance / info libre)

| Colonne | Type | Description |
|---|---|---|
| ID | Texte (clé, ex. `E001`) | Identifiant technique **stable**, jamais réutilisé ni renuméroté (indépendant du n° affiché dans le rapport) |
| Scope | Liste (`Config`) | EUS, M&A, … |
| Section | Liste | Projet / Incident / Decision / Risque / Opportunite / Besoin / Finance / Autre |
| NumeroAffiche | Texte | Le n° affiché dans le rapport (« Project 1 », « Incident 4 ») — peut être recalculé automatiquement à l'export |
| Titre | Texte | Intitulé court |
| Statut | Liste | Actif / Clôturé / Annulé / En pause |
| Owner | Texte | Responsable de l'item |
| Probabilite | Liste (Low/Medium/High) | Renseigné uniquement pour Section = Risque |
| ImpactPotentiel | Liste (Low/Medium/High) | Renseigné uniquement pour Section = Risque |
| ChampFixe1 | Texte long | Libellé contextuel selon Section : *Achieved Objectives* (Projet), *Impact* (Incident), *Reason* (Décision), *Expected Benefits* (Opportunité) |
| ChampFixe2 | Texte long | Libellé contextuel : *Next Steps* (Projet), *Mitigation Plan — cadre général* (Risque) |
| DateCreation | Date | |
| DateCloture | Date | Vide si l'item est encore actif |

### 3.2 Table `T_Journal` (une ligne = une mise à jour datée — remplace l'empilement manuel dans une cellule)

| Colonne | Type | Description |
|---|---|---|
| JournalID | Texte (clé) | |
| ElementID | Texte (FK → `T_Elements.ID`) | |
| Date | Date | Date de la mise à jour (remplace « Update DD/MM ») |
| Semaine | Texte (ex. `S28`) | Calculée automatiquement depuis Date, éditable |
| Auteur | Texte | |
| Texte | Texte long | Contenu de la mise à jour (une ligne du journal) |

### 3.3 Table `T_Config`

- Liste des scopes : Code, Nom affiché, Niveau de confidentialité (C1-Internal / C2-Restricted / …), couleur bandeau
- Semaine de référence courante (Année + n° de semaine), utilisée pour calculer « nouveauté de la semaine »
- Listes de valeurs contrôlées : Statut, Probabilité/Impact, Sections

## 4. Architecture du classeur

| Feuille | Rôle |
|---|---|
| `Dashboard` | KPI consolidés tous scopes + graphique |
| `Config` | Paramètres, listes de référence, semaine courante |
| `DB_Elements` | Table `T_Elements` (saisie) |
| `DB_Journal` | Table `T_Journal` (saisie) |
| `Rapport_<Scope>` (une par scope) | Restitution mise en page, générée par formules à partir des tables — **lecture seule**, ne pas saisir dedans |
| `Guide` | Mode d'emploi condensé |

La saisie se fait uniquement dans `DB_Elements` / `DB_Journal` (ou via un formulaire, cf. §5.1). Les feuilles `Rapport_*` ne sont que des vues calculées : on peut les régénérer/supprimer sans perte de données.

## 5. Fonctionnalités détaillées

### 5.1 Saisie
- Saisie directe dans les tableaux structurés (Excel Tables), avec listes déroulantes de validation sur Scope, Section, Statut, Probabilité, Impact.
- Option V2 : formulaire (UserForm VBA ou Power Apps) pour ajouter une entrée de journal sans ouvrir la feuille de données brute — évite les erreurs de saisie dans la mauvaise ligne/table.

### 5.2 Journal des mises à jour
- Chaque mise à jour = une nouvelle ligne dans `T_Journal`, jamais une modification du texte existant → historique intégral conservé et non réécrit.
- Tri naturel par date ; filtrage possible par élément, semaine, auteur.

### 5.3 Génération automatique du rapport par scope
- Sur `Rapport_<Scope>`, chaque section reprend la mise en page du gabarit actuel, mais chaque bloc « Completed Tasks » / « Current Status » / « Mitigation Plan » est calculé par formule :
  - Filtrer `T_Elements` sur `Scope` et `Section`,
  - Pour chaque élément, agréger son journal (`FILTER` + `TEXTJOIN`, trié par date décroissante) pour reconstituer le texte affiché,
  - Reconstituer le format « Update DD/MM — texte » automatiquement depuis les colonnes Date/Texte.
- Nécessite Excel avec fonctions dynamiques (FILTER, SORT, TEXTJOIN — Microsoft 365 / Excel 2021+). Alternative si version antérieure : requête Power Query qui matérialise le texte agrégé dans une colonne technique, rafraîchie à l'ouverture.

### 5.4 Mise en évidence des nouveautés de la semaine
- Colonne technique `MAJ_Semaine_Courante` (VRAI/FAUX) = date de la dernière entrée de journal de l'élément ≥ début de la semaine de référence (`Config`).
- Mise en forme conditionnelle sur `Rapport_<Scope>` : remplissage/texte coloré automatique pour tout élément mis à jour cette semaine — remplace le surlignage manuel actuel.

### 5.5 Report automatique des éléments non clôturés
- Un item (`Statut` ≠ Clôturé/Annulé) apparaît automatiquement dans le rapport de la semaine suivante sans ressaisie, jusqu'à ce que son statut soit changé dans `DB_Elements`.
- Un item clôturé sort automatiquement du rapport (ou passe dans une section « Clôturés récemment », optionnel).

### 5.6 Tableau de bord
KPI calculés par `COUNTIFS`/`SUMPRODUCT` sur `T_Elements` :
- Nombre de projets actifs par scope
- Nombre de risques Probabilité=High **et** Impact=High (risques critiques)
- Nombre d'incidents ouverts
- Nombre d'éléments mis à jour cette semaine / non mis à jour depuis N semaines (alerte staleness)
- Graphique de répartition des risques par Probabilité × Impact

### 5.7 Export et nommage
- Bouton d'export PDF par scope respectant la convention déjà en usage : `AAAA - Weekly report <SCOPE>_S<NN>.pdf`.
- Le n° de semaine et l'année sont repris automatiquement depuis `Config`.

### 5.8 Multi-scope et confidentialité
- Le bandeau de pied de page (« Sensitivity: C1-Internal / C2-Restricted ») est piloté par la table `Config` (un scope = un niveau), reporté automatiquement sur chaque `Rapport_<Scope>`.
- Ajout d'un nouveau scope = une ligne dans `Config` + duplication de la feuille `Rapport_Modele`, sans toucher au modèle de données.

## 6. Règles de gestion

- Un `ElementID` n'est jamais réutilisé, même après clôture ou suppression logique (garantit la traçabilité du journal historique).
- Le champ `NumeroAffiche` (« Project 1 », « Incident 4 ») n'est qu'un affichage : il peut être recalculé automatiquement par ordre de création au sein du couple (Scope, Section), pour éviter les trous ou doublons de numérotation constatés dans le gabarit actuel (ex. deux « Project 27 » distincts dans le rapport M&A source).
- La suppression physique d'une ligne dans `T_Elements` est déconseillée : préférer un `Statut = Annulé` pour conserver l'historique.

## 7. Contrôles de saisie

| Champ | Contrôle |
|---|---|
| Scope | Liste déroulante issue de `Config` |
| Section | Liste déroulante fixe |
| Statut | Liste déroulante fixe (Actif/Clôturé/Annulé/En pause) |
| Probabilite / ImpactPotentiel | Liste déroulante Low/Medium/High, obligatoire si Section=Risque |
| Date (journal) | Validation date, ≤ date du jour |
| ElementID (journal) | Doit exister dans `T_Elements` (validation par liste ou VBA) |

## 8. Automatisations recommandées (V1 → V2)

- **V1 (livrée en maquette)** : tables structurées + formules dynamiques + mise en forme conditionnelle + tableau de bord. Aucune macro requise.
- **V2 (optionnelle)** :
  - Macro « Nouvelle semaine » : incrémente `Config.Semaine`, archive un instantané (copie figée en valeurs) du rapport précédent dans un classeur d'archives.
  - Macro/bouton « Exporter en PDF » nommé automatiquement.
  - Renumérotation automatique de `NumeroAffiche`.
  - Alerte (mise en forme conditionnelle ou email via Power Automate) sur les risques High/High sans mise à jour depuis > 3 semaines.

## 9. Sécurité et confidentialité

- Le niveau de sensibilité (C1/C2) reste porté par la donnée (`Config`), pas codé en dur dans la mise en page, pour rester correct même si un scope change de classification.
- Protection des feuilles `Rapport_*` en lecture seule (protection de feuille Excel) pour éviter la saisie accidentelle hors du modèle de données.

## 10. Évolutions possibles

- Bascule vers Power BI / Power Apps si le nombre de scopes ou d'éléments devient important (les deux tables `T_Elements`/`T_Journal` sont directement réutilisables comme source).
- Historisation semaine par semaine dans un classeur d'archives séparé pour permettre une revue « ce qui a changé entre S27 et S28 » automatisée.

## 11. Correspondance avec la maquette livrée

Le fichier `Maquette_Outil_Reporting_Projets.xlsx` implémente ce modèle avec des données d'exemple (quelques projets, incidents, risques inspirés des scopes EUS/M&A) afin de valider le mécanisme : saisie dans `DB_Elements`/`DB_Journal` → mise à jour automatique de `Rapport_EUS` et `Rapport_MA` → surlignage des nouveautés → KPI sur `Dashboard`.
