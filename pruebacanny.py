import cv2
# Carga la imagen
imagen = cv2.imread('img.jpg', cv2.IMREAD_GRAYSCALE)  # Carga la imagen en escala de grises

# Aplica el algoritmo Canny
bordes = cv2.Canny(imagen, 50, 150)

cv2.imshow('Bordes', bordes)
cv2.waitKey(0)
cv2.destroyAllWindows()
