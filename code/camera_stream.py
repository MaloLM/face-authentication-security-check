import cv2
import paho.mqtt.client as mqtt
import json
import base64
from ultralytics import YOLO


def preprocess_image(frame):
    # Exemple simple de flip horizontal (peut être adapté)
    return cv2.flip(frame, 1)


def publish_frame(client, topic, frame):
    # Encodage de l'image en format JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    # Publier l'image au format base64
    message = json.dumps({"image": jpg_as_text})
    client.publish(topic, message)


def main():
    # Charger le modèle YOLOv8 pré-entraîné
    model = YOLO("../models/yolov8n-oiv7.pt", task='detect') 

    # Pipeline CSI pour accéder à la caméra sur Nvidia Jetson
    csi_pipeline = (
        "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1 ! "
        "nvvidconv flip-method=0 ! video/x-raw, format=BGRx ! videoconvert ! appsink"
    )

    # Initialiser la capture vidéo CSI
    cap = cv2.VideoCapture(csi_pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir le flux vidéo de la caméra CSI.")
        return

    # Configuration MQTT
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    client.loop_start()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de lire le flux vidéo.")
            break

        # Prétraiter l'image avant d'effectuer l'inférence
        processed_frame = preprocess_image(frame)

        # Effectuer l'inférence YOLOv8
        results = model(processed_frame)

        # Rechercher si un visage est détecté
        faces_detected = False
        for detection in results[0].boxes:
            if detection.cls == 0:  # YOLO class '0' correspond généralement à "personne"
                faces_detected = True
                break

        # Si un visage est détecté, publier l'image
        if faces_detected:
            print("Visage détecté, publication de l'image...")
            publish_frame(client, "camera/images", processed_frame)

        # Afficher les résultats annotés
        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 CSI Camera Inference", annotated_frame)

        # Quitter si 'q' est pressé
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
