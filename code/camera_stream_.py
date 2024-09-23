import paho.mqtt.client as mqtt
import base64
import json
import cv2
import numpy as np
import jetson.inference
import jetson.utils

# Configuration MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "camera/images"

# Initialisation du réseau de détection et de la caméra
source = "csi://0"  # Utilisation de la caméra CSI (ou /dev/video0)
net = jetson.inference.detectNet("facedetect", threshold=0.4)
camera = jetson.utils.gstCamera(1280, 720, source)

# Fonction pour publier l'image et les bounding boxes via MQTT
def publish_mqtt(image, bboxes):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Convertir l'image OpenCV en format JPEG
    _, buffer = cv2.imencode('.jpg', image)
    
    # Encoder l'image en base64
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Créer une structure JSON avec l'image et les bounding boxes
    message = {
        "image": image_base64,
        "bboxes": bboxes
    }
    
    # Publier le message sous forme de JSON sur le topic MQTT
    client.publish(MQTT_TOPIC, json.dumps(message))
    
    client.disconnect()

# Boucle principale de détection
def detection_loop():
    try:
        while True:  # Boucle infinie avec KeyboardInterrupt pour l'arrêter
            # Capture de l'image avec la caméra CSI
            img, width, height = camera.CaptureRGBA()
            
            # Exécuter la détection sur l'image capturée
            detections = net.Detect(img, width, height)
            
            bboxes = []
            # Vérifier s'il y a des détections de visages
            if len(detections) > 0:
                # Convertir l'image RGBA Jetson en format compatible avec OpenCV (BGR)
                img_bgr = jetson.utils.cudaToNumpy(img, width, height, 4)  # Convertir en tableau NumPy
                img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2BGR)  # Convertir RGBA -> BGR
                
                # Parcourir les détections et extraire les bounding boxes
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

                # Publier l'image et les bounding boxes via MQTT
                publish_mqtt(img_bgr, bboxes)
    
    except KeyboardInterrupt:
        print("Interruption clavier détectée. Fermeture du programme.")

# Fonction principale
if __name__ == "__main__":
    detection_loop()
