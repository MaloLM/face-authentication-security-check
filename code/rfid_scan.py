import time
import paho.mqtt.client as mqtt

MQTT_PUB_TOPIC = "rfid/id"
TMP_IDEA = '234654723'  # tmp ID while RFID Scan is not implemented
TMP_TIMER = 25  # seconds


def on_connect(client, userdata, flags, rc):
    """
    Callback function triggered when the MQTT client connects to the broker.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: User-defined data passed when setting the callback.
        flags: Response flags sent by the broker.
        rc (int): Connection result code (0 means success).

    Prints the connection result and subscribes to the relevant topics, if any.
    """
    topic_to_sub = []
    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)

    print("Connect to broker with code: {:.0f}".format(rc))


def publish_message(client, topic, message):
    """
    Publishes a message to a specified MQTT topic.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        topic (str): The MQTT topic where the message will be published.
        message (str): The message to be published, in string format.
    """
    client.publish(topic, message)


def main():

    client = mqtt.Client()

    client.on_connect = on_connect

    client.connect("localhost", 1883, 60)

    client.loop_start()

    try:
        start = time.time()
        while True:
            now = time.time()
            if now - start > TMP_TIMER:
                publish_message(client, MQTT_PUB_TOPIC, TMP_IDEA)  # tmp
                start = time.time()

    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
