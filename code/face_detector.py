# 3 - programme 'Face detector' récupère l'ID sur le broker 'camera/capture' puis, pour X images (X a definir), récupère X images sur le broker 'camera/images'.
# Pour chaque image, tant qu'un ou plusieurs visages suffisamment grands ne sont pas détectés, prendre la dernière image sur le broker.
# 3.1 - l'image contient un ou plusieurs visages suffisamment grand -> selectionner le visage le plus grand et publier l'image, la bbox du visage et l'ID sur 'camera/face'.
# 3.alt - toutes les images n'ont pas détecté de visage suffisamment grand -> programme 'Face detector' publie 'couleur rouge clignotante' sur le broker 'led/instruct'.

# 2 - programme 'DB Check' récupère l'ID sur le broker, vérifie que l'ID est l'une des clés du fichier JSON.
# 2.1 - l'ID correspond a une clé du fichier JSON -> le programme 'DB Check' publie l'ID sur le broker 'camera/capture'.
# 2.alt - l'ID ne correspond pas a une clé du fichier JSON -> le programme 'DB Check' publie 'couleur rouge clignotante' sur le broker 'led/instruct'.
import json
import cv2
import numpy as np
import base64
import time
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Connecté au broker avec le code de résultat {rc}")

    topic_to_sub = [("camera/capture", 0), ("camera/images", 0)]
    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)


# Fonction pour publier un message sur un ou plusieurs topics
def publish_message(client, topic, message):
    client.publish(topic, message)
    print(f"Message publié sur {topic}: {message}")

# Fonction Callback qui s'exécute lorsqu'un message est reçu sur un topic


def on_message(client, userdata, msg):
    global start_capturing

    if msg.topic == "camera/capture":
        # Quand un message est reçu sur camera/capture, démarrer l'acquisition d'images
        start_capturing = True
        print("Capture d'images demandée...")

    elif msg.topic == "camera/images" and start_capturing:
        start_capturing = False
        # Réception d'une image sur camera/images
        message = json.loads(msg.payload.decode())
        jpg_as_text = message["image"]
        jpg_original = base64.b64decode(jpg_as_text)

        # Convertir en format d'image OpenCV
        nparr = np.frombuffer(jpg_original, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Ajouter l'image à la mémoire tampon
        image_buffer.append(frame)

        if len(image_buffer) >= 10:
            process_images(client)


def process_images(client):
    global start_capturing, image_buffer

    print(f"Traitement de {len(image_buffer)} images...")
    for frame in image_buffer:
        # TODO: Ajouter ici le modèle de détection faciale

        # Si un visage est détecté, afficher un message et arrêter l'acquisition
        faces_detected = False  # Placeholder pour la détection
        if faces_detected:
            print("Visage détecté, arrêt de la capture.")
            break

    # Réinitialiser les variables pour la prochaine capture
    start_capturing = False
    image_buffer = []


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


if __name__ == "__main__":
    main()
