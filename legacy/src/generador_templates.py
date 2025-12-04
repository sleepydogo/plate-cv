
#  
#   Este archivo se encarga de generar los recortes de digitos de patente
#   para generar los respectivos templates...
#

import os 
import cv2
import numpy as np
import matplotlib.pyplot as plt

class static_variables:
    contador = 0

def recortar_imagen(img, selec):
    recorte = img[
    selec[1] :
    selec[1] + selec[3] ,
    selec[0] : 
    selec[0] + selec[2] 
    ].copy()
    cv2.imwrite(f'/home/tom/universidad/plate-cv/resources/templates/no_margen/template{static_variables.contador}.jpg', recorte)
    static_variables.contador = static_variables.contador + 1
    print('Recorte guardado exitosamente!')
    return 0

def recortar_extremos_patente(patente_binarizada):
    altura, ancho = patente_binarizada.shape[:2]
    THRESHOLD = 100
    filas_a_eliminar = []
    for i in range(altura):
        suma = 0
        for j in range(ancho): 
            suma = suma + patente_binarizada[i][j]
        if (suma/ancho) <  THRESHOLD: 
            filas_a_eliminar.append(i)
    filas_a_eliminar.extend(range(altura-15,altura))
    patente = np.delete(patente_binarizada, filas_a_eliminar, 0)
    return patente

def recortar_digitos(img):
    altura, ancho = img.shape[:2]
    _, labels, stats, centroids = cv2.connectedComponentsWithStats(~img)
    stats_letras = []
    area_max = (altura*ancho)/6
    area_min = (ancho*altura)/62
    for i in range(0, len(stats)):
        x, y, w, h, area = stats[i]
        if area_max > area > area_min:
            stats_letras.append(stats[i])
            recortar_imagen(img, stats[i])
    return 0

def main():    
    for i in os.listdir('/home/tom/universidad/plate-cv/resources/dataset_generado'):
        print(i)
        imagen = cv2.imread('/home/tom/universidad/plate-cv/resources/dataset_generado/'+i, cv2.IMREAD_GRAYSCALE)
        _, patente_binarizada = cv2.threshold(imagen, 140, 255, cv2.THRESH_BINARY)
        imagen = recortar_extremos_patente(patente_binarizada)
        imagen = recortar_digitos(imagen.copy())
    return 0 


if __name__ == '__main__':
    main()



