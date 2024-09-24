import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
import face_recognition

# load file



# get face encodings



# add to encoding database

test_images = []

for image in test_images:
	face_locations = face_recognition.face_locations(image)
	face_encodings = face_recognition.face_encodings(image, face_locations)

	