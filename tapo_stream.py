"""
tapo_stream.py
---------------
Récupère et affiche le flux vidéo d'une caméra TP-Link Tapo C200 via RTSP.
Permet de visualiser le flux en direct, de prendre des captures d'écran
(touche 's') et d'enregistrer une vidéo (touche 'r' pour démarrer/arrêter).
Quitte avec la touche 'q'.

Prérequis :
  - Un "compte caméra" (identifiant / mot de passe RTSP) créé dans
    l'application Tapo : Paramètres avancés > Compte caméra.
    (différent du compte TP-Link utilisé pour l'application)
  - La librairie opencv-python installée (pip install opencv-python)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import cv2

# Résolution HD (stream1) par défaut, SD (stream2) plus légère en bande passante
STREAM_PATHS = {"hd": "stream1", "sd": "stream2"}


def build_rtsp_url(ip: str, username: str, password: str, quality: str = "hd") -> str:
    """Construit l'URL RTSP du flux Tapo C200 à partir des identifiants et de l'IP."""
    stream_path = STREAM_PATHS[quality]
    return f"rtsp://{username}:{password}@{ip}:554/{stream_path}"


def open_stream(rtsp_url: str) -> cv2.VideoCapture:
    """Ouvre le flux RTSP et vérifie qu'il est bien accessible."""
    # FFMPEG gère nativement le protocole RTSP et l'authentification dans l'URL
    capture = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not capture.isOpened():
        print("Erreur : impossible de se connecter au flux RTSP.")
        print("Vérifiez l'IP, les identifiants du compte caméra et le réseau.")
        sys.exit(1)
    return capture


def watch_stream(rtsp_url: str, output_dir: Path) -> None:
    """
    Affiche le flux vidéo en direct dans une fenêtre.
    Commandes clavier :
      q : quitter
      s : sauvegarder une capture d'écran (.jpg)
      r : démarrer / arrêter un enregistrement vidéo (.avi)
    Se reconnecte automatiquement si le flux est interrompu.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    capture = open_stream(rtsp_url)
    writer = None

    print("Flux connecté. Fenêtre vidéo active : q=quitter, s=capture, r=enregistrer.")

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print("Flux interrompu, tentative de reconnexion...")
                capture.release()
                capture = open_stream(rtsp_url)
                continue

            cv2.imshow("Tapo C200", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            elif key == ord("s"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                snapshot_path = output_dir / f"snapshot_{timestamp}.jpg"
                cv2.imwrite(str(snapshot_path), frame)
                print(f"Capture sauvegardée : {snapshot_path}")

            elif key == ord("r"):
                if writer is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    video_path = output_dir / f"enregistrement_{timestamp}.avi"
                    height, width = frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    writer = cv2.VideoWriter(str(video_path), fourcc, 20.0, (width, height))
                    print(f"Enregistrement démarré : {video_path}")
                else:
                    writer.release()
                    writer = None
                    print("Enregistrement arrêté.")

            if writer is not None:
                writer.write(frame)
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Affiche le flux vidéo d'une caméra Tapo C200 via RTSP.")
    parser.add_argument("--ip", help="Adresse IP de la caméra (ex: 192.168.1.50)")
    parser.add_argument("--username", help="Identifiant du compte caméra RTSP")
    parser.add_argument("--password", help="Mot de passe du compte caméra RTSP")
    parser.add_argument(
        "--quality", choices=["hd", "sd"], default="hd", help="Qualité du flux (hd=stream1, sd=stream2, défaut: hd)"
    )
    parser.add_argument(
        "--output-dir", default="captures", help="Répertoire de sauvegarde des captures/enregistrements"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    ip = args.ip or input("Adresse IP de la caméra : ").strip()
    username = args.username or input("Identifiant du compte caméra RTSP : ").strip()
    password = args.password or input("Mot de passe du compte caméra RTSP : ").strip()

    url = build_rtsp_url(ip, username, password, args.quality)
    watch_stream(url, Path(args.output_dir))
