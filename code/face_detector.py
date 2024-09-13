# 3 - programme 'Face detector' récupère l'ID sur le broker 'camera/capture' puis, pour X images (X a definir), récupère X images sur le broker 'camera/images'.
# Pour chaque image, tant qu'un ou plusieurs visages suffisamment grands ne sont pas détectés, prendre la dernière image sur le broker.
# 3.1 - l'image contient un ou plusieurs visages suffisamment grand -> selectionner le visage le plus grand et publier l'image, la bbox du visage et l'ID sur 'camera/face'.
# 3.alt - toutes les images n'ont pas détecté de visage suffisamment grand -> programme 'Face detector' publie 'couleur rouge clignotante' sur le broker 'led/instruct'.
