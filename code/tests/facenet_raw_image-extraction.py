
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

    display.RenderOnce(img, width, height)
    display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

