import cv2
import numpy as np

# Carga una imagen binaria o una imagen en escala de grises
imagen = cv2.imread('img.jpg', cv2.IMREAD_GRAYSCALE)  # Cambia la bandera según corresponda

# Define el kernel o elemento estructurante para la dilatación
kernel = np.ones((5, 5), np.uint8)  # Puedes ajustar el tamaño y la forma del kernel según tus necesidades

# Aplica la dilatación
imagen_dilatada = cv2.dilate(imagen, kernel, iterations=1)

# Muestra la imagen original y la imagen dilatada
cv2.imshow('Imagen Original', imagen)
cv2.imshow('Imagen Dilatada', imagen_dilatada)
cv2.waitKey(0)
cv2.destroyAllWindows()
