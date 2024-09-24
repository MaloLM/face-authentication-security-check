import json
import numpy as np
import matplotlib.pyplot as plt
import face_recognition

# load file

image_path = '../../data/malmal.png'
malmal = face_recognition.load_image_file(image_path)

# get face encodings


def get_value_from_json(file_path, key):
    # Ouvrir le fichier JSON
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Vérifier si la clé existe
    if key in data:
        return data[key]  # Retourner la valeur associée à la clé
    else:
        return None  # Retourner None si la clé n'existe pas


file_path = '../../data/embeddings.json'
id = '234654723'

malmal_encoding = get_value_from_json(file_path, id)

# add to encoding database

known_face_encodings = [malmal_encoding]
known_face_names = ["Malmal"]

test_images = [malmal]

# compute face recognition

for image in test_images:
    # Detect face locations and encodings
    face_locations = face_recognition.face_locations(image)
    new_face_encodings = face_recognition.face_encodings(image, face_locations)

    # Plotting the image using matplotlib
    plt.figure(figsize=(8, 6))
    plt.imshow(image)

    # Loop through each detected face and its encoding
    for i, new_encoding in enumerate(new_face_encodings):
        # Get the face location
        top, right, bottom, left = face_locations[i]

        # Compare with known faces
        matches = face_recognition.compare_faces(
            known_face_encodings, new_encoding)
        face_distances = face_recognition.face_distance(
            known_face_encodings, new_encoding)

        # Find the best match
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            bbox_color = (0, 1, 0)  # Green for identified faces
        else:
            name = "Unknown"
            bbox_color = (1, 0, 0)  # Red for unknown faces

        # Draw a rectangle around the face
        rect = plt.Rectangle((left, top), right - left, bottom -
                             top, fill=False, color=bbox_color, linewidth=2)
        plt.gca().add_patch(rect)

        # Add the name annotation
        plt.text(left, top - 10, name, color=bbox_color,
                 fontsize=12, weight="bold")

    # Show the image with annotations
    plt.axis("off")
    plt.show()
