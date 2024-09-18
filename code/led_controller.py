# 5. Programme 'LED controller' récupère le comportement de la LED a afficher sur le broker 'led/instruct'
#   5.1 - affiche clignotant rouge pendant 4 secondes si la valeur sur le broker est 'auth_failure'
#   5.2 - affiche clignotant vert pendant 4 secondes si la valeur sur le broker est 'auth_success'
#   5.3 - affiche rouge par défaut

import json
import time
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Connecté au broker avec le code de résultat {rc}")

    topic_to_sub = [('led/instruct', 0)]
    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)


# Fonction pour publier un message sur un ou plusieurs topics
# def publish_message(client, topic, message):
#    client.publish(topic, message)
#    print(f"Message publié sur {topic}: {message}")


def on_message(client, userdata, msg):
    """
    Fonction Callback qui s'exécute lorsqu'un message est reçu sur un topic
    """
    message = json.loads(msg.payload.decode())
    print("Message: ", message)


def update_color(color, behavior):
    pass


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
        while True:
            pass

    except KeyboardInterrupt:
        # Arrêter la boucle et déconnecter proprement
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
