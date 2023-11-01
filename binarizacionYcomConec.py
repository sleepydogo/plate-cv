import cv2
import numpy as np

img_leer = "img1.jpg"
# Carga la imagen
imgColor = cv2.imread(img_leer)

imagen = cv2.imread(
    img_leer, cv2.IMREAD_GRAYSCALE
)  # Carga la imagen en escala de grises


# Binarizacion

umbral_global = 150


# Aplica la binarización en toda la imagen
_, imagen_binarizada = cv2.threshold(imagen, umbral_global, 255, cv2.THRESH_BINARY)

##cv2.imshow("Imagen Binarizada con Componentes Conectados", imagen_binarizada)
# Convierte la imagen binarizada a escala de grises

# Aplica la detección de componentes conectados en la imagen binarizada en escala de grises
_, labels, stats, centroids = cv2.connectedComponentsWithStats(imagen_binarizada)


##Si descomento esto puedo ver todos los componentes detectados antes de filtrarlos
""" for i in range(1, len(stats)):
    x, y, w, h, area = stats[i]
    cv2.rectangle(imgColor, (x, y), (x + w, y + h), (0, 255, 0), 2)


cv2.imshow("Imagen Binarizada con Componentes Conectados", imgColor)
 """


##FILRO DE COMPONENTES

## ANCHO APROXIMADO DE PATENTE 120PX
## ALTO APROXIMADO DE PATENTE 40PX
## COEFICIENTE APROXIMADO ANCHO/ALTO 3

##PARA CALCULAR EL AREA:
## Ancho aproximado 150px
## Alto aproximado 60px
## Area aproximada 9000px

##Area total de la imagen = 211455px
##Por lo tanto ponemos un maximo de 100, y un minimo de 23
##Con 100 de relacion funciona para la primera imagen que use, img_funcionando.
##Voy a modificar un poco esto para ver si funciona con otras imagenes
##Con 150 detecta dos cosas en la segunda imagen de prueba. Sigo testeando.
##Con la tercera imagen tuve que aumentar mas el area para que detecte la patente. Con 300 funciona.(Detecta 2)
##Imagen 4 la detecta bien :)

##Filtro por relacion de aspecto. Si no cumple con la relacion de aspecto, se elimina
##Filtro por relacion de areas

area_total_imagen = imagen_binarizada.size
for label in range(1, len(stats)):
    ancho = stats[label, cv2.CC_STAT_WIDTH]
    alto = stats[label, cv2.CC_STAT_HEIGHT]
    area_componente = stats[label, cv2.CC_STAT_AREA]

    relacion_aspecto = ancho / alto if ancho != 0 else 0
    relacion_area = area_total_imagen / area_componente
    if not (2.8 < relacion_aspecto < 5):
        labels[
            labels == label
        ] = 0  # Eliminar componente basado en la relación de aspecto
        stats[label] = 0  # Eliminar las estadísticas del componente

    if not (23 < relacion_area < 300):
        labels[labels == label] = 0  # Eliminar componente basado en la relación de área
        stats[label] = 0  # Eliminar las estadísticas del componente


# Convertir la matriz labels a un tipo de datos compatible
labels = np.uint8(labels)

# Remover los componentes eliminados de labels y stats
new_labels, _, new_stats, _ = cv2.connectedComponentsWithStats(labels)


# Dibuja rectángulos alrededor de los componentes conectados en la imagen original
for i in range(1, len(new_stats)):
    x, y, w, h, area = new_stats[i]
    cv2.rectangle(imgColor, (x, y), (x + w, y + h), (0, 255, 0), 2)


cv2.namedWindow("Imagen Mostrada", cv2.WINDOW_NORMAL)
cv2.imshow("Imagen Mostrada", imgColor)
cv2.resizeWindow("Imagen Mostrada", 800, 600)
cv2.waitKey(0)
cv2.destroyAllWindows()
