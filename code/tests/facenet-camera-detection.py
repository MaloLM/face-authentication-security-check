import jetson.inference
import jetson.utils

source = "csi://0" # "/dev/video0"
net = jetson.inference.detectNet("facedetect", threshold=0.4)
camera = jetson.utils.gstCamera(1280, 720, source)
display = jetson.utils.glDisplay()

while display.IsOpen():
	img, width, height = camera.CaptureRGBA()
	detections = net.Detect(img, width, height)
	print(detections)

	#for elem in detections:
	#	print(vars(elem), "/n")

	# print(type(detections)) # list
	for detection in detections:
		print(int(detection.Left))
		



	display.RenderOnce(img, width, height)
	display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))