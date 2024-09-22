import time
from blinkstick import blinkstick
import paho.mqtt.client as mqtt



def set_static(bstick, color_name: str):
    bstick.set_color(name=color_name)

def set_blinking(bstick, color_name, nb_blink=8):
    bstick.blink(channel=0, index=0, name=color_name, repeats=nb_blink, delay = 150)


def set_pulse(bstick, color_name):
    raise NotImplementedError

def on_connect(client, userdata, flags, rc):
    """
    Callback qui s'exécute lorsque le client se connecte au broker
    """
    print(f"Connecté au broker avec le code de résultat {rc}")

    topic_to_sub = [("led/instruct", 0)]
    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)


def on_message(client, userdata, msg):
    """
    Fonction Callback qui s'exécute lorsqu'un message est reçu sur un topic
    """
    global my_bstick
    global behaviors

    print(f"Message reçu sur le topic {msg.topic}: {msg.payload.decode()}")

    key = msg.payload.decode()


    message = {
        "key": key,
        "embeddings": value
    }

    message_json = json.dumps(message)


    if ("color", "behavior") in message_json.keys():
        color = message_json['color']
        behavior = message_json['behavior']

        if my_bstick._names_to_hex[color]:

            if behavior in behaviors:
                behaviors[behavior](my_bstick, color)
            else:
                print(f"behaviour {message_json['behavior']} does not exist")
        else:
            print(f"color {color} does not exist")
    else:
        print("('color', 'behavior') n'est pas dans les clés du message")




my_bstick = blinkstick.find_first()

behaviors = {
    'static': set_static,
    'blinking' : set_blinking,
    'pulse': set_pulse
}


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
            set_static(my_bstick, "darkred")
            time.sleep(1)
            set_blinking(my_bstick, "darkred")

    except KeyboardInterrupt:
        # Arrêter la boucle et déconnecter proprement
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()

