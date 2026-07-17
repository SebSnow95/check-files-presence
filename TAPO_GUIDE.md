# tapo_stream.py — Guide d'utilisation

## 1. Objectif

`tapo_stream.py` récupère et affiche le flux vidéo en direct d'une caméra
TP-Link Tapo C200 via le protocole **RTSP**, directement en réseau local
(pas besoin du cloud TP-Link ni de l'application Tapo une fois configuré).

## 2. Prérequis

- Python 3.10 ou supérieur
- La librairie `opencv-python` :
  ```bash
  pip install -r requirements.txt
  ```
- Un **compte caméra** RTSP créé dans l'application Tapo :
  1. Ouvrir l'application Tapo
  2. Sélectionner la caméra C200
  3. Paramètres avancés (icône engrenage) > **Compte caméra**
  4. Créer un identifiant / mot de passe (différent du compte TP-Link)
- L'adresse IP locale de la caméra (visible dans l'app Tapo, ou via le
  routeur / un scan réseau type `arp -a`)
- Le PC et la caméra doivent être sur le **même réseau local**

## 3. Lancement

En mode interactif (le script demande les informations) :

```bash
python tapo_stream.py
```

Ou directement en ligne de commande :

```bash
python tapo_stream.py --ip 192.168.1.50 --username monuser --password monpass
```

Options disponibles :

| Option | Description |
|---|---|
| `--ip` | Adresse IP de la caméra |
| `--username` | Identifiant du compte caméra RTSP |
| `--password` | Mot de passe du compte caméra RTSP |
| `--quality` | `hd` (stream1, défaut) ou `sd` (stream2, plus léger) |
| `--output-dir` | Répertoire de sauvegarde des captures/enregistrements (défaut : `captures`) |

## 4. Commandes clavier (fenêtre vidéo)

| Touche | Action |
|---|---|
| `q` | Quitter |
| `s` | Sauvegarder une capture d'écran (.jpg) |
| `r` | Démarrer / arrêter un enregistrement vidéo (.avi) |

## 5. Dépannage

| Problème | Piste |
|---|---|
| Connexion refusée / timeout | Vérifier l'IP de la caméra et que le PC est sur le même réseau |
| Authentification échouée | Recréer le compte caméra dans l'app Tapo, vérifier identifiant/mot de passe |
| Flux qui coupe régulièrement | Wi-Fi faible signal ou bande passante ; essayer `--quality sd` |
| Aucune image mais connexion OK | Vérifier qu'aucune autre application (app Tapo, NVR) n'utilise déjà le flux RTSP simultanément |
