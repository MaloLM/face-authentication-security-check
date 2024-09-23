# 5. Programme 'LED controller' récupère le comportement de la LED a afficher sur le broker 'led/instruct'
#   5.1 - affiche clignotant rouge pendant 4 secondes si la valeur sur le broker est 'auth_failure'
#   5.2 - affiche clignotant vert pendant 4 secondes si la valeur sur le broker est 'auth_success'
#   5.3 - affiche rouge par défaut

import json
import time
from blinkstick import blinkstick
import paho.mqtt.client as mqtt


def set_static(bstick, color_name: str, duration: int):
    
    if duration is None:
        bstick.set_color(name=color_name)
    else:
        bstick.set_color(name=color_name)
        time.sleep(duration)
        reset_led()


def set_blinking(bstick, color_name, duration=None, nb_blink=8):


    bstick.blink(channel=0, index=0, name=color_name, repeats=nb_blink, delay = 100)
    reset_led()


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

    message_json = msg.payload.decode()

    message_json = json.loads(message_json)


    if 'color' in message_json.keys() and 'behavior' in message_json.keys():
        color = message_json['color']
        behavior = message_json['behavior']
        duration = message_json['duration'] if 'duration' in message_json.keys() else None

        if my_bstick._names_to_hex[color]:
            execute_bahavior(my_bstick, behavior, color, duration)

        else:
            print(f"color {color} does not exist")
    else:
        print("('color', 'behavior') n'est pas dans les clés du message")


def execute_bahavior(my_bstick, behavior, *args, **kwargs):
    if behavior in behaviors:
        behaviors[behavior](my_bstick, *args, **kwargs)
    else:
        print(f"behaviour {message_json['behavior']} does not exist")

default_color = "darkred"
my_bstick = blinkstick.find_first()

behaviors = {
    'static': set_static,
    'blinking' : set_blinking,
    'pulse': set_pulse
}


def reset_led():
    global default_color
    set_static(my_bstick, default_color, None)


def main():
    global my_bstick

    reset_led()

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

        my_bstick.turn_off()


if __name__ == "__main__":
    main()
