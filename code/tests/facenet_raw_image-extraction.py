import cv2
import jetson_inference
import jetson_utils

# Initialisation du réseau de détection et de la caméra
source = "csi://0"  # Utilisation de la caméra CSI
net = jetson_inference.detectNet("facedetect", threshold=0.4)
camera = jetson_utils.gstCamera(1280, 720, source)


def main():
    try:
        while True:
            # Capture de l'image avec la caméra CSI
            img, width, height = camera.CaptureRGBA()

            # Exécuter la détection sur l'image capturée
            detections = net.Detect(img, width, height)

            # Convertir l'image RGBA capturée en tableau compatible OpenCV (BGR)
            img_bgr = jetson_utils.cudaToNumpy(
                img, width, height, 4)  # Convertir en tableau NumPy
            # Convertir RGBA -> BGR
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2BGR)

            # Afficher l'image brute dans une fenêtre OpenCV
            cv2.imshow("Image Brute - Détection de Visages", img_bgr)

            # Interrompre la boucle si l'utilisateur appuie sur 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Interruption clavier détectée. Fermeture du programme.")

    finally:
        # Libérer les ressources
        camera.Close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
