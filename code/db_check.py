# 2 - programme 'DB Check' récupère l'ID sur le broker, vérifie que l'ID est l'une des clés du fichier JSON.
# 2.1 - l'ID correspond a une clé du fichier JSON -> le programme 'DB Check' publie l'ID sur le broker 'camera/capture'.
# 2.alt - l'ID ne correspond pas a une clé du fichier JSON -> le programme 'DB Check' publie 'couleur rouge clignotante' sur le broker 'led/instruct'.
import json
import paho.mqtt.client as mqtt


def get_value_from_json(file_path, key):
    # Ouvrir le fichier JSON
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Vérifier si la clé existe
    if key in data:
        return data[key]  # Retourner la valeur associée à la clé
    else:
        return None  # Retourner None si la clé n'existe pas

# Callback qui s'exécute lorsque le client se connecte au broker


def on_connect(client, userdata, flags, rc):
    print(f"Connecté au broker avec le code de résultat {rc}")

    topic_to_sub = [("rfid/id", 0), ("topic/test2", 0)]
    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)


# Fonction pour publier un message sur un ou plusieurs topics
def publish_message(client, topic, message):
    client.publish(topic, message)
    print(f"Message publié sur {topic}: {message}")

# Fonction Callback qui s'exécute lorsqu'un message est reçu sur un topic


def on_message(client, userdata, msg):
    print("g ressu hein mesag: ", msg)
    if msg.topic == 'rfid/id':
        print(f"Message reçu sur le topic {msg.topic}: {msg.payload.decode()}")

        key = msg.payload.decode()

        file_path = './embeddings.json'

        value = get_value_from_json(file_path, key)

        if value:
            message = {
                "key": key,
                "embeddings": value
            }

            message_json = json.dumps(message)

            print(f"Valeur trouvée pour la clé {key}: {value}")
            publish_message(client, "camera/capture", message_json)
        else:
            print(f"La clé {key} n'existe pas dans le fichier JSON")
            publish_message(client, "led/instruct", "Bonjour led/instruct")


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
