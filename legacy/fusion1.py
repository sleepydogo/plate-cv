import cv2
import numpy as np

# Carga la imagen
imagen = cv2.imread('img.jpg', cv2.IMREAD_GRAYSCALE)  # Carga la imagen en escala de grises

# Divide la imagen en regiones/zonas (por ejemplo, en 4 partes)
alto, ancho = imagen.shape
num_filas = 2  # Número de filas de regiones
num_columnas = 2  # Número de columnas de regiones
alto_region = alto // num_filas
ancho_region = ancho // num_columnas

# Define los umbrales para cada región (en este ejemplo, son valores arbitrarios)
umbrales = [150 , 150, 150, 150]  # Debes proporcionar los umbrales específicos para cada región

# Inicializa una imagen de salida
imagen_binarizada = np.zeros_like(imagen)

# Aplica la binarización en cada región
for fila in range(num_filas):
    for columna in range(num_columnas):
        region = imagen[fila * alto_region:(fila + 1) * alto_region, columna * ancho_region:(columna + 1) * ancho_region]
        umbral = umbrales[fila * num_columnas + columna]
        _, binarizada_region = cv2.threshold(region, umbral, 255, cv2.THRESH_BINARY)
        imagen_binarizada[fila * alto_region:(fila + 1) * alto_region, columna * ancho_region:(columna + 1) * ancho_region] = binarizada_region

# Muestra la imagen binarizada

bordes = cv2.Canny(imagen_binarizada, 50, 150)

cv2.imshow('Bordes', bordes)
cv2.waitKey(0)
cv2.destroyAllWindows()



