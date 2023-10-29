import cv2
import numpy as np

# Carga la imagen
imagen = cv2.imread('img.jpg')

# Divide la imagen en regiones/zonas (por ejemplo, en 2 partes)
num_filas = 2  # Número de filas de regiones
num_columnas = 2  # Número de columnas de regiones
alto, ancho, _ = imagen.shape
alto_region = alto // num_filas
ancho_region = ancho // num_columnas

# Define los umbrales para cada región (debes proporcionar umbrales específicos)
umbrales = [150, 150, 150, 150]  # Debes ajustar estos valores

# Inicializa una imagen de salida
imagen_binarizada = np.zeros_like(imagen)

# Aplica la binarización en cada región
for fila in range(num_filas):
    for columna in range(num_columnas):
        region = imagen[fila * alto_region:(fila + 1) * alto_region, columna * ancho_region:(columna + 1) * ancho_region]
        umbral = umbrales[fila * num_columnas + columna]
        _, binarizada_region = cv2.threshold(region, umbral, 255, cv2.THRESH_BINARY)
        imagen_binarizada[fila * alto_region:(fila + 1) * alto_region, columna * ancho_region:(columna + 1) * ancho_region] = binarizada_region

# Convierte la imagen binarizada a escala de grises
imagen_binarizada_gris = cv2.cvtColor(imagen_binarizada, cv2.COLOR_BGR2GRAY)

# Aplica la detección de componentes conectados en la imagen binarizada en escala de grises
_, labels, stats, centroids = cv2.connectedComponentsWithStats(imagen_binarizada_gris)

# Dibuja rectángulos alrededor de los componentes conectados en la imagen original
for i in range(1, len(stats)):
    x, y, w, h, area = stats[i]
    cv2.rectangle(imagen, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Muestra la imagen resultante
cv2.imshow('Imagen Binarizada con Componentes Conectados', imagen_binarizada)
cv2.waitKey(0)
cv2.destroyAllWindows()
