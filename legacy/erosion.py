import cv2
import numpy as np

# Carga una imagen binaria o una imagen en escala de grises
imagen = cv2.imread('img.jpg', cv2.IMREAD_GRAYSCALE)  # Cambia la bandera según corresponda

# Define el kernel o elemento estructurante para la erosión
kernel = np.ones((5, 5), np.uint8)  # Puedes ajustar el tamaño y la forma del kernel según tus necesidades

# Aplica la erosión
imagen_erodada = cv2.erode(imagen, kernel, iterations=1)

# Muestra la imagen original y la imagen erodada
cv2.imshow('Imagen Original', imagen)
cv2.imshow('Imagen Erodada', imagen_erodada)
cv2.waitKey(0)
cv2.destroyAllWindows()
