# 1 - utilisateur scan RFID.
# 1.1 - programme 'RFID Scan' retourne l'ID du tag de l'utilisateur.
# 1.alt - programme 'RFID Scan' publie 'couleur rouge clignotante' sur le broker 'led/instruct'.

import time
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Connecté au broker avec le code de résultat {rc}")

    topic_to_sub = []
    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)


# Fonction pour publier un message sur un ou plusieurs topics
def publish_message(client, topic, message):
    client.publish(topic, message)
    print(f"Message publié sur {topic}: {message}")

# Fonction Callback qui s'exécute lorsqu'un message est reçu sur un topic


def on_message(client, userdata, msg):
    print("Message: ", msg)


def main():

    client = mqtt.Client()

    # Attacher les callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connexion au broker
    client.connect("localhost", 1883, 60)

    # Lancer la boucle réseau dans un thread séparé
    client.loop_start()

    # Garder le programme en vie pour écouter les messages
    try:
        start = time.time()
        while True:
            now = time.time()
            if now - start > 10:
                publish_message(client, "led/instruct", "Bonjour led/instruct")
                publish_message(client, "rfid/id", "234654723")
                start = time.time()

    except KeyboardInterrupt:
        # Arrêter la boucle et déconnecter proprement
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
