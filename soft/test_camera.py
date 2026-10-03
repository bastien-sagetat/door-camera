#!/usr/bin/env python3

import cv2
import time
import os

CAMERA = "/dev/video4"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

VIDEO_FILE = "test.mp4"
FRAME_INTERVAL = 5  # secondes


# Dossier pour les captures périodiques
os.makedirs("frames", exist_ok=True)

# Ouverture de la caméra
cap = cv2.VideoCapture(CAMERA, cv2.CAP_V4L2)

if not cap.isOpened():
    raise RuntimeError(f"Impossible d'ouvrir {CAMERA}")

# Demande le format MJPEG à la caméra
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

# Vérification des paramètres réellement utilisés
real_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
real_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
real_fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Caméra : {real_width}x{real_height} @ {real_fps:.1f} FPS")

# Codec vidéo
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    VIDEO_FILE,
    fourcc,
    FPS,
    (real_width, real_height)
)

if not writer.isOpened():
    cap.release()
    raise RuntimeError("Impossible de créer le fichier vidéo")

print(f"Enregistrement : {VIDEO_FILE}")
print("Une image sera sauvegardée toutes les 5 secondes.")
print("Appuie sur 'q' pour arrêter.")

last_capture = time.monotonic()
frame_count = 0

try:
    while True:

        ret, frame = cap.read()

        if not ret:
            print("Erreur lors de la lecture de la caméra")
            break

        # 1. Enregistrement de CHAQUE frame
        writer.write(frame)
        frame_count += 1

        # 2. Capture périodique
        now = time.monotonic()

        if now - last_capture >= FRAME_INTERVAL:
            timestamp = time.strftime("%Y%m%d_%H%M%S")

            filename = f"frames/frame_{timestamp}.jpg"

            cv2.imwrite(filename, frame)

            print(f"Frame sauvegardée : {filename}")

            last_capture = now

        # Affichage
        display = cv2.resize(frame, (960, 540))

        cv2.imshow("PS5268 - Recording", display)

        # q = quitter
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    print("\nArrêt...")

    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    print(f"Frames enregistrées : {frame_count}")
    print(f"Vidéo : {VIDEO_FILE}")