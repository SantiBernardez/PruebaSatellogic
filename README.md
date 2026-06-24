# Reconocimiento de imágenes y ubicación de vértices.
Pequeña API para ubicar una imagen de *plantilla* en una *escena*. y devuelve la localización de sus vértices en *escena*. 
## Requerimientos
La API solo necesita los paquetes numpy y opencv. Junto a las dependiencias de ambos claro.
Para pruebas y benchmark se requieren _time_ y _resource_, los cuales vienen por defecto en python.
## Archivos
El archivo de API es _solo detector.py_. Se agrega un archivo de prueba que toma las 2 imágenes enviadas por correo y genera un nuevo archivo _imagen\_vértices.tif_, la cual es la imagen de prueba enviada por correo pero con los vértices del semicirculo marcados.
También incluyo otro archivo con los requerimientos _requirements.txt_.
## Funcionamiento
La API se llama **buscar\_vértices\_en\_escena** , toma 2 argumentos obligatorios __path\_plantilla__, __path\_escena__ , donde se indican la ubicacón de los archivos de *plantilla* y *escena*, respectivamente. Ambas imágenes deben de estar en los formatos soportados por opencv.
Hay otro argumento opcional __benchmark__, el cual indica si se quiere medir los tiempos de lectura y procesado.
## Algoritmo.
Como hipotesis se asume que las imágenes tanto de *plantilla* y *escena* son una figura blanca sobre fondo negro.
El primer paso es convertir las imágenes a una escala de blanco y negro pura, eliminadno ruido.
Ya que las imágenes pueden ser muy grandes primero se busca la zona de interés reduciendo las imágenes a un 5% de su tamaño original.
Luego se ubican los contornos de ambas imágenes. En el caso de *plantilla* se toma el más grande. Para *escena* se compara mediante momentos Hu con todos los encontrados.
Despúes de este proceso se selecciona el contorno de *escena* con mejor match.
Una vez identificada la forma se analiza la imagen de *escena* original (sin reducción de tamaño). Comparando el contorno de mayor tamaño.
Para encontrar los vértices es necesario utilizar una aproximación polinomial, la cual reduce significativamente la cantidad de puntos a operar.
Los vértices A y B son aquellos puntos a mayor distancia entre si. Mientras que C es el punto a mayor distancia de el segmento AB.
Y con la magia del procesamiento de señales y geometría se encuentran los vértices.
## Resultado
La API retorna 4 Valores como tupla: (Found,pt\_A,pt\_B,pt\_C). 
### Si Found es True
Entonces pt\_A,pt\_B,pt\_C son la ubicación de los vetrices.
### Si Found es False
Entonces la busqueda falló
#### Si pt\_A,pt\_B,pt\_C son None 
Falló la busqueda de figura en *plantilla*.
#### Si pt\_A,pt\_B,pt\_C son -1
Falló busqueda de figuras en escena. 
#### Si pt\_A,pt\_B,pt\_C son Inf
Entonces no hay contornos en la zona de interés de *escena*.
 


