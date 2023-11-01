import cv2
import numpy as np

# Carga la imagen
imagen = cv2.imread(
    "img0.jpg", cv2.IMREAD_GRAYSCALE
)  # Carga la imagen en escala de grises

umbral_global = 150

# Convierte la imagen a escala de grises si es a color
if len(imagen.shape) > 2:
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
else:
    imagen_gris = imagen

# Aplica la binarización en toda la imagen
_, imagen_binarizada = cv2.threshold(imagen_gris, umbral_global, 255, cv2.THRESH_BINARY)

# Muestra la imagen binarizada
cv2.imshow("Imagen Binarizada", imagen_binarizada)
cv2.waitKey(0)
cv2.destroyAllWindows()
