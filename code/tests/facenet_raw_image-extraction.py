
import jetson.inference
import cv2
import jetson.utils


source = "csi://0"  # Utilisation de la caméra CSI
net = jetson.inference.detectNet("facedetect", threshold=0.4)
camera = jetson.utils.gstCamera(1280, 720, source)
display = jetson.utils.glDisplay()

while display.IsOpen():
    img, width, height = camera.CaptureRGBA()
    detections = net.Detect(img, width, height)

    # Convertir l'image RGBA capturée en tableau compatible OpenCV (BGR)
    #img_bgr = jetson.utils.cudaToNumpy(img, width, height, 4)  # Convertir en tableau NumPy
    # Convertir RGBA -> BGR
    #img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2BGR)

    # Afficher l'image brute dans une fenêtre OpenCV
    # cv2.imshow("Image Brute - Détection de Visages", img)

    # Interrompre la boucle si l'utilisateur appuie sur 'q'
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

    display.RenderOnce(img, width, height)
    display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

