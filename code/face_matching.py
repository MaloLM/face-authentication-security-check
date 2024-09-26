import json
import cv2
import base64
import numpy as np
import face_recognition
import paho.mqtt.client as mqtt
from utils import get_value_from_json

# Nombre maximum de tentatives pour récupérer une nouvelle image
MAX_ATTEMPTS = 3
MQTT_IMAGE_STREAM = "camera/images"
MQTT_CAPTURE = "camera/capture"
file_path = '../data/embeddings.json'
capture = False

# Variables global
attempt_count = 0
embeddings_id = None  # ID de l'embedding récupéré via 'camera/capture'


# def on_connect(client, userdata, flags, rc):
#     """
#     Callback déclenché lors de la connexion au broker MQTT.

#     Args:
#         client (paho.mqtt.client.Client): Instance du client MQTT.
#         userdata: Données utilisateur.
#         flags: Drapeaux passés par le broker.
#         rc (int): Code de résultat de connexion (0 pour succès).

#     Le client est abonné au topic défini par `MQTT_CAPTURE` et le code de connexion est imprimé.
#     """
#     client.subscribe(MQTT_CAPTURE)
#     print("Connect to broker with code: {:.0f}".format(rc))


def on_connect(client, userdata, flags, rc):
    """
    Callback triggered when connecting to the MQTT broker.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: User-defined data passed when setting the callback.
        flags: Flags sent by the broker.
        rc (int): Connection result code (0 means success).

    Subscribes the client to the topic defined by `MQTT_CAPTURE` and prints the connection result code.
    """
    topic_to_sub = [(MQTT_CAPTURE, 0)]

    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)

    print("Connect to broker with code: {:.0f}".format(rc))


def publish_message(client, topic, message, retain=False):
    """
    Publishes a message to a specified MQTT topic.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        topic (str): The MQTT topic to publish the message to.
        message (str): The message to be published, typically in JSON format.
        retain (bool, optional): Whether the message should be retained on the broker. Defaults to False.

    The message is published to the given topic, and a confirmation message is printed.
    """
    client.publish(topic, message, retain=retain)
    print(f"Message publié sur {topic}: {message}")


def check_embedding(incomming_embedding, id_embeddings, emb_id):
    """
    Checks whether an incoming embedding matches a known embedding.

    Args:
        incomming_embedding (list): List of face embeddings received from the detected face.
        id_embeddings (list): Known face embeddings associated with the ID.
        emb_id (str): ID to compare the embeddings against.

    Returns:
        bool: True if the incoming embedding matches the known embedding, otherwise False.
    """
    known_face_encodings = [id_embeddings]  # dirty
    known_face_names = [emb_id]  # dirty

    # Loop through each detected face and its encoding
    for i, new_encoding in enumerate(incomming_embedding):

        # Compare with known faces
        matches = face_recognition.compare_faces(
            known_face_encodings, new_encoding)
        face_distances = face_recognition.face_distance(
            known_face_encodings, new_encoding)

        # Find the best match
        best_match_index = np.argmin(face_distances)
        print(best_match_index)

        if matches[best_match_index]:
            if known_face_names[best_match_index] == emb_id:
                return True
            else:
                return False
        else:
            return False


def fetch_last_retained_image(client):
    """
    Fetches the last retained image from the 'camera/images' topic.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.

    Subscribes the client to the image stream to retrieve the most recent image.
    """
    client.subscribe()


def on_message(client, userdata, msg):
    """
    Callback triggered when a message is received on a subscribed topic.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: User-defined data passed when setting the callback.
        msg (paho.mqtt.client.MQTTMessage): The received MQTT message, containing the payload and topic.

    Handles incoming capture notifications, processes the received image, detects faces, and compares facial embeddings.
    """
    global attempt_count, embeddings_id, capture

    if msg.topic == MQTT_CAPTURE:
        print("-- Incomming capture notification")
        data = json.loads(msg.payload.decode())
        embeddings_id = data['id']

        attempt_count = 0
        capture = True
        fetch_last_retained_image(client)

    elif msg.topic == MQTT_IMAGE_STREAM and capture:
        # Réception de la dernière image retenue sur 'camera/images'
        message = json.loads(msg.payload.decode())
        jpg_as_text = message["image"]
        bboxes = message["bboxes"]

        # Vérifier si des bounding boxes sont présentes
        if len(bboxes) > 0:
            # Décodage de l'image base64
            jpg_original = base64.b64decode(jpg_as_text)
            nparr = np.frombuffer(jpg_original, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Sélectionner la plus grande bbox (le plus grand visage)
            largest_bbox = max(
                bboxes, key=lambda bbox: bbox["width"] * bbox["height"])

            face_locations = face_recognition.face_locations(frame)
            incomming_face_encodings = face_recognition.face_encodings(
                frame, face_locations)

            print(incomming_face_encodings)

            id_embeddings = get_value_from_json(file_path, embeddings_id)

            # Comparer l'embedding associé au visage (logique à ajouter)
            if check_embedding(incomming_face_encodings, id_embeddings, embeddings_id):
                print("Embedding correspondant trouvé.")
                # Si l'embedding correspond, arrêter et notifier le contrôleur LED
                client.unsubscribe(MQTT_IMAGE_STREAM)
                message = {
                    "color": "green",
                    "behavior": "blinking"
                }
                publish_message(client, "led/instruct", json.dumps(message))
                capture = False

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
                        "color": "darkred",
                        "behavior": "blinking"
                    }
                    publish_message(client, "led/instruct",
                                    json.dumps(message))
                    client.unsubscribe(MQTT_IMAGE_STREAM)
                    attempt_count = 0
                    capture = False
        else:
            print("Aucune bounding box détectée dans l'image.")
            attempt_count += 1
            if attempt_count >= MAX_ATTEMPTS:
                message = {
                    "color": "yellow",
                    "behavior": "blinking"
                }
                publish_message(client, "led/instruct", json.dumps(message))
                client.unsubscribe(MQTT_IMAGE_STREAM)
                attempt_count = 0
                capture = False


def main():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    client.loop_forever()


if __name__ == "__main__":
    main()
