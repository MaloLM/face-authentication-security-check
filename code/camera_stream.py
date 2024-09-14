import cv2
import paho.mqtt.client as mqtt
import json
import base64


def preprocess_image(frame):
    # Exemple simple de flip horizontal
    return cv2.flip(frame, 1)


def publish_frame(client, topic, frame):
    # Encodage de l'image en format JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    # Publier l'image au format base64
    message = json.dumps({"image": jpg_as_text})
    client.publish(topic, message)


def main():
    # Initialisation de la capture vidéo (0 = caméra par défaut)
    cap = cv2.VideoCapture(0)

    # Configuration MQTT
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    client.loop_start()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Prétraiter l'image avant publication
        processed_frame = preprocess_image(frame)

        # Publier l'image prétraitée
        publish_frame(client, "camera/images", processed_frame)

        # Attendre un court instant avant de publier la prochaine image
        cv2.waitKey(100)  # 10 FPS

    cap.release()
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
