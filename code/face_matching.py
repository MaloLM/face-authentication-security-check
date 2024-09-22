# 4 - programme 'Face matching' récupère l'ID, l'embeddings sur le broker 'camera/capture' puis récupère les dernières X images et les bboxes sur le broker 'camera/images'.
#    4.1 - l'image contient un ou plusieurs visages suffisamment grand -> selectionner le visage le plus grand et compare les embeddings résultantes avec les embeddings du fichier JSON associé à l'ID.
#       4.1.1 - les embeddings matchent -> le programme publie 'couleur verte clignotante' sur le broker 'led/instruct'
#       4.1.alt - les embeddings ne matchent pas -> le programme publie 'couleur rouge clignotante' sur le broker 'led/instruct'
#    4.alt - Pas d'image publiées dans les X dernières secondes -> programme 'Face detector' publie 'couleur rouge clignotante' sur le broker 'led/instruct'.

import json
import cv2
import numpy as np
import base64
import paho.mqtt.client as mqtt

# Nombre maximum de tentatives pour récupérer une nouvelle image
MAX_ATTEMPTS = 5

# Variables globales
attempt_count = 0


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


def check_embedding(frame):
    """
    Fonction qui vérifie si l'embedding correspond (toujours False pour l'instant)
    """
    # Placeholder pour la vérification des embeddings
    # À remplacer par la logique réelle d'appariement d'embeddings
    if attempt_count == 4:
        return True
    else:
        return False


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
    global attempt_count

    if msg.topic == "camera/capture":
        # Lorsque le message est reçu sur 'camera/capture', démarrer le processus de vérification
        attempt_count = 0
        fetch_last_retained_image(client)

    elif msg.topic == "camera/images":
        # Réception de la dernière image retenue sur 'camera/images'
        message = json.loads(msg.payload.decode())
        jpg_as_text = message["image"]

        # Décodage de l'image base64
        jpg_original = base64.b64decode(jpg_as_text)
        nparr = np.frombuffer(jpg_original, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Vérifier si l'embedding correspond
        if check_embedding(frame):
            print(True)
            print("Embedding correspondant trouvé.")
            # Si l'embedding correspond, arrêter
            client.unsubscribe("camera/images")

            # notify lED controller
            message = {
                "color": "green",
                "behaviour": "blink"
            }

            message_json = json.dumps(message)

            publish_message(client, "led/instruct", message_json)

        else:
            print(f"Embedding non correspondant. Tentative {attempt_count + 1}/{MAX_ATTEMPTS}")
            attempt_count += 1
            print(attempt_count)
            if attempt_count < MAX_ATTEMPTS:
                # Si l'embedding ne correspond pas et qu'il reste des tentatives, récupérer la nouvelle dernière image
                fetch_last_retained_image(client)
            else:
                # Si le nombre maximum de tentatives est atteint, arrêter
                print("Nombre maximum de tentatives atteint. Arrêt de la vérification.")
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
