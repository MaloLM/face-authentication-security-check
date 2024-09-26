import json
import time
import paho.mqtt.client as mqtt
from blinkstick import blinkstick


def set_static(bstick, color_name: str, duration: int = None):
    """
    Sets the BlinkStick LED to a static color.

    Args:
        bstick (blinkstick.BlinkStick): The BlinkStick device instance.
        color_name (str): The name of the color to set the LED (e.g., "red", "blue").
        duration (int): The duration (in seconds) to keep the LED on. If None, the LED remains static indefinitely.
    """
    if duration is None:
        bstick.set_color(name=color_name)
    else:
        bstick.set_color(name=color_name)
        time.sleep(duration)
        reset_led()


def set_blinking(bstick, color_name, duration: int = 2, delay: int = 0.1):
    """
    Sets the BlinkStick LED to blink for a specified duration and delay between blinks.

    Args:
        bstick (blinkstick.BlinkStick): The BlinkStick device instance.
        color_name (str): The name of the color for the LED during the blink (e.g., 'red', 'blue').
        duration (int, optional): Total duration of the blinking effect in seconds. Default is 2 seconds.
        delay (float, optional): Delay in seconds between each blink cycle (on and off). Default is 0.1 seconds.

    The function calculates the number of blinks based on the duration and delay, 
    then triggers the blinking effect on the BlinkStick device. After blinking, 
    the LED is reset to its default state using `reset_led()`.
    """
    repeats = duration / (delay*2)
    bstick.blink(channel=0, index=0, name=color_name,
                 repeats=repeats, delay=delay)
    reset_led()


def set_pulse(bstick, color_name):
    """
    Sets the BlinkStick LED to a pulsing behavior (not implemented).

    Args:
        bstick (blinkstick.BlinkStick): The BlinkStick device instance.
        color_name (str): The name of the color to pulse.

    Raises:
        NotImplementedError: This function is not implemented yet.
    """
    raise NotImplementedError


def on_connect(client, userdata, flags, rc):
    """
    Callback function triggered when the MQTT client connects to the broker.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: User-defined data passed when setting the callback.
        flags: Response flags sent by the broker.
        rc (int): The connection result. 0 indicates success.

    Subscribes the client to the 'led/instruct' topic upon connection.
    """
    topic_to_sub = [("led/instruct", 0)]
    if len(topic_to_sub) > 0:
        client.subscribe(topic_to_sub)

    print("Connect to broker with code: {:.0f}".format(rc))


def on_message(client, userdata, msg):
    """
    Callback function triggered when a message is received on a subscribed topic.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: User-defined data passed when setting the callback.
        msg (paho.mqtt.client.MQTTMessage): The received message object containing the payload and topic.

    This function decodes the message, checks for 'color' and 'behavior' keys, 
    and executes the corresponding behavior on the BlinkStick device.
    """
    global my_bstick, behaviors

    message_json = msg.payload.decode()
    message_json = json.loads(message_json)

    if 'color' in message_json.keys() and 'behavior' in message_json.keys():
        color = message_json['color']
        behavior = message_json['behavior']
        duration = message_json['duration'] if 'duration' in message_json.keys(
        ) else None

        if my_bstick._names_to_hex[color]:
            execute_bahavior(my_bstick, behavior, color, duration)

        else:
            print(f"Color {color} does not exist")
    else:
        print("Missing 'color' or 'behavior' key/value")


def execute_bahavior(my_bstick, behavior, *args, **kwargs):
    """
    Executes the specified behavior on the BlinkStick device.

    Args:
        my_bstick (blinkstick.BlinkStick): The BlinkStick device instance.
        behavior (str): The behavior to execute ('static', 'blinking', or 'pulse').
        *args: Additional arguments required for the behavior function.
        **kwargs: Additional keyword arguments required for the behavior function.

    This function checks if the behavior exists and runs it; otherwise, it prints an error.
    """
    if behavior in behaviors:
        behaviors[behavior](my_bstick, *args, **kwargs)
    else:
        print(f"behaviour '{behavior}' does not exist")


default_color = "darkred"
my_bstick = blinkstick.find_first()

behaviors = {
    'static': set_static,
    'blinking': set_blinking,
    'pulse': set_pulse
}


def reset_led():
    """
    Resets the BlinkStick LED to the default static color.

    This function resets the LED to the 'default_color' which is 'darkred', 
    and keeps it static (i.e., no blinking or pulsing).
    """
    global default_color
    set_static(my_bstick, default_color)


def main():
    global my_bstick  # necessary ?

    reset_led()

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

        my_bstick.turn_off()


if __name__ == "__main__":
    main()
