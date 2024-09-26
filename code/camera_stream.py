import json
import cv2
import base64
import jetson_utils
import jetson_inference
import paho.mqtt.client as mqtt

# MQTT configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "camera/images"

# Camera and detection network init
CSI_SOURCE = "csi://0"
net = jetson_inference.detectNet("facedetect", threshold=0.5)
camera = jetson_utils.gstCamera(1280, 720, CSI_SOURCE)


def publish_message(image, bboxes):
    """
    Publishes an image and associated bounding boxes to a specified MQTT topic.

    Args:
        image (numpy.ndarray): The image captured by the camera in OpenCV format (BGR).
        bboxes (list): A list of bounding boxes where each box is represented as a dictionary 
                       containing 'left', 'top', 'width', 'height', 'center_x', and 'center_y'.

    The image is first encoded in JPEG format and then base64 encoded before being published
    to the MQTT broker under the topic defined by `MQTT_TOPIC`.
    """
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Convert OenCV image to jpeg
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    message = {
        "image": image_base64,
        "bboxes": bboxes
    }

    client.publish(MQTT_TOPIC, json.dumps(message), retain=True)
    # client.disconnect()  # ???


def are_faces_detected(detections):
    """
    Checks if any faces were detected in the current frame.

    Args:
        detections (list): A list of detection objects returned by the detection network.

    Returns:
        bool: True if one or more faces are detected, False otherwise.
    """
    return True if len(detections) > 0 else False


def main():
    try:
        nb_publish = 0
        while True:

            img, width, height = camera.CaptureRGBA()

            detections = net.Detect(img, width, height, overlay="none")

            if are_faces_detected(detections):
                # Convert RGBA image to OpenCV compatible (BGR)
                img_bgr = jetson_utils.cudaToNumpy(img, width, height, 4)

                img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2BGR)

                # Go through detections and extract bounding boxes properties
                bboxes = []
                for detection in detections:
                    bbox = {
                        "left": int(detection.Left),
                        "top": int(detection.Top),
                        "width": int(detection.Width),
                        "height": int(detection.Height),
                        "center_x": int(detection.Center[0]),
                        "center_y": int(detection.Center[1])
                    }
                    bboxes.append(bbox)

                publish_message(img_bgr, bboxes)
                nb_publish += 1

                print("published message {:.0f} with bboxes".format(i))

    except KeyboardInterrupt:
        print("Interruption clavier détectée. Fermeture du programme.")


if __name__ == "__main__":
    main()
