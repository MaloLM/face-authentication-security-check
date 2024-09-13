# 2 - programme 'DB Check' récupère l'ID sur le broker, vérifie que l'ID est l'une des clés du fichier JSON.
# 2.1 - l'ID correspond a une clé du fichier JSON -> le programme 'DB Check' publie l'ID sur le broker 'camera/capture'.
# 2.alt - l'ID ne correspond pas a une clé du fichier JSON -> le programme 'DB Check' publie 'couleur rouge clignotante' sur le broker 'led/instruct'.
