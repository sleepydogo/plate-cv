import cv2
import numpy as np


def filtro_cambio_color_en_proporciones(imagen_binaria, proporciones):
    total_transiciones = 0

    for prop in proporciones:
        # Extraer la fila específica
        fila_a_analizar = imagen_binaria[int(imagen_binaria.shape[0] * prop), :]

        # Calcular las diferencias en la fila
        diferencias = np.abs(np.diff(fila_a_analizar))

        # Sumar las diferencias en la fila
        total_transiciones += np.sum(diferencias)

    return total_transiciones

## Imagen debe ser pasada en grayscale
def detector(imgColor, imagen, verbose):
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
    _, new_labels, new_stats, _ = cv2.connectedComponentsWithStats(labels)

    proporciones_a_analizar = [1 / 4, 1 / 2, 3 / 4]

    # Rango de cantidad de diferencias permitidas
    rango_cantidad_diferencias = (30, 90)

    # Nuevos labels y stats que almacenarán solo los componentes que pasan el nuevo filtro
    nuevos_labels = np.zeros_like(labels)
    nuevos_stats = []
    indices_validos = []

    # Iterar sobre las estadísticas de los nuevos componentes
    for i in range(1, len(new_stats)):
        x, y, w, h, area = new_stats[i]

        # Reiniciar el total de transiciones para cada objeto
        total_transiciones = 0

        # Extraer la región de interés (ROI) de la imagen binarizada
        roi_a_analizar = imagen_binarizada[y : y + h, x : x + w]

        # Aplicar el filtro en las proporciones específicas
        total_transiciones = filtro_cambio_color_en_proporciones(
            roi_a_analizar, proporciones_a_analizar
        )

        print(total_transiciones)

        valor_final = total_transiciones/(w+1)

        print(valor_final)

        # Verificar si la suma total de transiciones está dentro del rango
        if not (
            rango_cantidad_diferencias[0]
            <= valor_final
            <= rango_cantidad_diferencias[1]
        ):
            # Imprimir la cantidad total de transiciones para cada objeto
            print(f"Objeto {i}: Total de transiciones = {total_transiciones}")

            new_labels[
                new_labels == i
            ] = 0  # Eliminar componente basado en la relación de aspecto
            new_stats[i] = 0  # Eliminar las estadísticas del componente


    # Convertir la matriz nuevos_labels a un tipo de datos compatible
    new_labels = np.uint8(new_labels)

    # Remover el componente 0 (fondo) de los nuevos labels y stats
    nuevos_labels, _, nuevos_stats, _ = cv2.connectedComponentsWithStats(new_labels)


    # Después de la sección donde se aplica el filtro
    print("Número de objetos válidos:", len(nuevos_stats))


    for i in range(1, len(nuevos_stats)):
        x, y, w, h, area = nuevos_stats[i]
        cv2.rectangle(imgColor, (x, y), (x + w, y + h), (0, 255, 0), 2)


    # Dibuja rectángulos alrededor de los componentes conectados en la imagen original
    # for i in range(1, len(new_stats)):
    #    x, y, w, h, area = new_stats[i]
    #    cv2.rectangle(imgColor, (x, y), (x + w, y + h), (0, 255, 0), 2)


    if verbose:
        resized = cv2.resize(imgColor, (700,700), interpolation = cv2.INTER_AREA)
        cv2.imshow("Imagen Mostrada", resized)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return nuevos_stats
