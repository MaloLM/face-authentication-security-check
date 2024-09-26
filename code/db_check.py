import json
import paho.mqtt.client as mqtt
from utils import get_value_from_json

MQTT_SUB_TOPIC = "rfid/id"


def on_connect(client, userdata, flags, rc):
    """
    Callback function triggered when the MQTT client connects to the broker.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: User-defined data passed when setting the callback.
        flags: Response flags sent by the broker.
        rc (int): Connection result. 0 indicates success.

    Subscribes the client to the `MQTT_SUB_TOPIC` upon successful connection and prints the result code.
    """
    topic_to_sub = [(MQTT_SUB_TOPIC, 0)]

    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)

    print("Connect to broker with code: {:.0f}".format(rc))


def publish_message(client, topic, message):
    """
    Publishes a given message to a specified MQTT topic.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        topic (str): The MQTT topic to publish to.
        message (str): The message to publish, usually in JSON format.
    """
    client.publish(topic, message)


def on_message(client, userdata, msg):
    """
    Callback function triggered when a message is received on a subscribed topic.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: User-defined data passed when setting the callback.
        msg (paho.mqtt.client.MQTTMessage): The received MQTT message containing the payload and topic.

    Retrieves a value from a JSON file using the received message payload (as the key) and publishes the
    corresponding value if found. Additionally, sends instructions to an LED controller based on the result.
    """
    # if msg.topic == 'MQTT_SUB_TOPIC':
    key = msg.payload.decode()

    file_path = '../data/embeddings.json'

    value = get_value_from_json(file_path, key)

    if value:
        message = {
            "id": key,
            "embeddings": value
        }

        message_json = json.dumps(message)

        send_to_led_controller(client, "blue", "static", 0.2)

        publish_message(client, "camera/capture", message_json)

    else:
        send_to_led_controller(client, "darkred", "blinking")


def send_to_led_controller(client, color: str, behavior: str, duration=None):
    """
    Sends a control message to the LED controller over MQTT.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        color (str): The color to display on the LED (e.g., 'blue', 'darkred').
        behavior (str): The LED behavior (e.g., 'static', 'blinking').
        duration (float, optional): Duration for the LED action (used if behavior is 'static'). Default is None.

    Publishes a message to the "led/instruct" topic, instructing the LED client to change color and behavior.
    """
    message = {
        "color": color,
        "behavior": behavior,
        "duration": duration
    }

    message_json = json.dumps(message)
    publish_message(client, "led/instruct", message_json)


def main():

    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    client.loop_start()

    try:
        while True:
            pass

    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
