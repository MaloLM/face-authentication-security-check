import json
import cv2
import numpy as np
import base64
import paho.mqtt.client as mqtt
import dlib

# Nombre maximum de tentatives pour récupérer une nouvelle image
MAX_ATTEMPTS = 5
# Remplace avec ton modèle si besoin
LANDMARK_MODEL_PATH = "shape_predictor_68_face_landmarks.dat"

# Initialisation du détecteur de landmarks de dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(LANDMARK_MODEL_PATH)

# Variables globales
attempt_count = 0
embeddings_id = None  # ID de l'embedding récupéré via 'camera/capture'


def on_connect(client, userdata, flags, rc):
    """
    Fonction appelée à la connexion au broker MQTT
    """
    print(f"Connecté au broker avec le code de résultat {rc}")

    # S'abonner au topic 'camera/capture'
    client.subscribe("camera/capture")


def publish_message(client, topic, message, retain=False):
    """
    Fonction pour publier un message sur un topic MQTT (option "retained" possible)
    """
    client.publish(topic, message, retain=retain)
    print(f"Message publié sur {topic}: {message}")


def check_embedding(embedding):
    """
    Fonction qui vérifie si l'embedding correspond (toujours False pour l'instant)
    """
    # Placeholder pour la logique réelle de matching des embeddings
    # Comparaison des embeddings extraits avec ceux de l'ID reçu
    # Ici, True ou False est renvoyé en fonction du matching des embeddings
    if attempt_count == 4:
        return True
    else:
        return False


def extract_landmarks(image, bbox):
    """
    Extraire les landmarks faciaux d'une image dans une région délimitée par une bbox
    """
    # Conversion de la bbox en rectangle compatible avec dlib
    dlib_rect = dlib.rectangle(int(bbox["left"]),
                               int(bbox["top"]),
                               int(bbox["left"] + bbox["width"]),
                               int(bbox["top"] + bbox["height"]))

    # Détecter les landmarks
    shape = predictor(image, dlib_rect)

    # Extraire les coordonnées des landmarks sous forme de liste de tuples
    landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]
    return landmarks


def fetch_last_retained_image(client):
    """
    Fonction pour récupérer la dernière image retenue
    """
    print("Récupération de la dernière image retenue sur le topic 'camera/images'...")
    # S'abonner temporairement pour recevoir le message retenu
    client.subscribe("camera/images")


def on_message(client, userdata, msg):
    """
    Callback qui s'exécute lorsqu'un message est reçu sur un topic
    """
    global attempt_count, embeddings_id

    if msg.topic == "camera/capture":
        # Lorsqu'un message est reçu sur 'camera/capture', démarrer le processus
        data = json.loads(msg.payload.decode())
        embeddings_id = data['id']  # Récupérer l'ID et les embeddings
        print(f"ID reçu: {embeddings_id}")
        attempt_count = 0
        fetch_last_retained_image(client)

    elif msg.topic == "camera/images":
        # Réception de la dernière image retenue sur 'camera/images'
        message = json.loads(msg.payload.decode())
        jpg_as_text = message["image"]
        bboxes = message["bboxes"]

        # Décodage de l'image base64
        jpg_original = base64.b64decode(jpg_as_text)
        nparr = np.frombuffer(jpg_original, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Vérifier si des bounding boxes sont présentes
        if len(bboxes) > 0:
            # Sélectionner la plus grande bbox (le plus grand visage)
            largest_bbox = max(
                bboxes, key=lambda bbox: bbox["width"] * bbox["height"])

            # Extraire les landmarks du visage le plus grand
            landmarks = extract_landmarks(frame, largest_bbox)
            print(f"Landmarks extraits: {landmarks}")

            # Comparer l'embedding associé au visage (logique à ajouter)
            if check_embedding(landmarks):
                print("Embedding correspondant trouvé.")
                # Si l'embedding correspond, arrêter et notifier le contrôleur LED
                client.unsubscribe("camera/images")
                message = {
                    "color": "green",
                    "behaviour": "blink"
                }
                publish_message(client, "led/instruct", json.dumps(message))

            else:
                print(f"Embedding non correspondant. Tentative {
                      attempt_count + 1}/{MAX_ATTEMPTS}")
                attempt_count += 1
                if attempt_count < MAX_ATTEMPTS:
                    # Si l'embedding ne correspond pas, récupérer la nouvelle dernière image
                    fetch_last_retained_image(client)
                else:
                    print("Nombre maximum de tentatives atteint. Embedding non trouvé.")
                    message = {
                        "color": "red",
                        "behaviour": "blink"
                    }
                    publish_message(client, "led/instruct",
                                    json.dumps(message))
                    client.unsubscribe("camera/images")
        else:
            print("Aucune bounding box détectée dans l'image.")
            attempt_count += 1
            if attempt_count >= MAX_ATTEMPTS:
                message = {
                    "color": "red",
                    "behaviour": "blink"
                }
                publish_message(client, "led/instruct", json.dumps(message))
                client.unsubscribe("camera/images")


def main():
    client = mqtt.Client()

    # Associer les callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connexion au broker
    client.connect("localhost", 1883, 60)

    # Lancer la boucle réseau
    client.loop_forever()


if __name__ == "__main__":
    main()
