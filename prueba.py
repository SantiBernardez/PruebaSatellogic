# test_detector.py
import time
import resource
import cv2
from detector import buscar_vertices_en_escena

# Configura aquí los nombres de tus archivos reales
PATH_PLANTILLA = "patron.bmp"
PATH_ESCENA = "imagen.tif"
PATH_SALIDA = "imagen_vertices.tif"

def ejecutar_prueba(PATH_PLANTILLA,PATH_ESCENA,PATH_SALIDA):
    
        print("Ejecutando detección matemática de vértices...")
        
        #Aplicar funcion
        Found,pt_A, pt_B, pt_C = buscar_vertices_en_escena(PATH_PLANTILLA,PATH_ESCENA,benchmark=True)
        memoria_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        #tiempo_total_ms = (tiempo_fin - tiempo_inicio) * 1000 # Convertir a milisegundos
        memoria_mb = memoria_kb / 1024.0
        if not Found:
                print(f'Busqueda fallida para plantilla:{PATH_PLANTILLA} y escena:{PATH_ESCENA}')
                if pt_A==-1:
                        print('Razón:No se encuentra en plantilla en escena')
                elif pt_A==None:
                        print('Razón:No se encontró figura en plantilla')
                else:
                        print('Razón:Error no implementado')
        print("\n Coordenadas encontradas (Sub-píxel float32):")
        print(f"Extremo de Arco A : X={pt_A[0]:.2f}, Y={pt_A[1]:.2f}")
        print(f"Extremo de Arco B : X={pt_B[0]:.2f}, Y={pt_B[1]:.2f}")
        print(f"Esquina 90° C    : X={pt_C[0]:.2f}, Y={pt_C[1]:.2f}")
        
        #Cargar magen original
        img_resultado = cv2.imread(PATH_ESCENA)
        if img_resultado is None:
            print("Error: No se pudo cargar la imagen de escena para dibujar.")
            return
        print(f"\n [BENCHMARK DE HARDWARE]")
        #print(f" Tiempo neto del algoritmo: {tiempo_total_ms:.2f} ms")
        print(f" Consumo máximo de RAM:     {memoria_mb:.2f} MB")
        # Dibujar los puntos (Casteamos a int solo al dibujar ya que las funciones de dibujo exigen píxeles enteros)
        centro_A = (int(pt_A[0]), int(pt_A[1]))
        centro_B = (int(pt_B[0]), int(pt_B[1]))
        centro_C = (int(pt_C[0]), int(pt_C[1]))
        
        # Parámetros del dibujo: cv2.circle(imagen, centro, radio, color_BGR, grosor)
        # Usamos -1 en grosor para que los círculos se pinten completamente rellenos
        cv2.circle(img_resultado, centro_A, 6, (0, 0, 255), -1)  # ROJO para Extremo A
        cv2.circle(img_resultado, centro_B, 6, (0, 255, 0), -1)  # VERDE para Extremo B
        cv2.circle(img_resultado, centro_C, 6, (255, 0, 0), -1)  # AZUL para Esquina C

        # Dibujar etiquetas de texto pequeñas al lado de cada punto
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img_resultado, "A", (centro_A[0] + 10, centro_A[1] - 10), font, 0.5, (0, 0, 255), 1)
        cv2.putText(img_resultado, "B", (centro_B[0] + 10, centro_B[1] - 10), font, 0.5, (0, 255, 0), 1)
        cv2.putText(img_resultado, "C (90 deg)", (centro_C[0] + 10, centro_C[1] - 10), font, 0.5, (255, 0, 0), 1)

        #Guardar la imagen en el almacenamiento
        cv2.imwrite(PATH_SALIDA, img_resultado)
        print(f"\n Éxito: Imagen guardada correctamente como '{PATH_SALIDA}'")
        
"""except FileNotFoundError as fnf:
        print(f"\n Error de Archivo: {fnf}")
    except Exception as e:
        print(f"\n Ocurrió un error durante la ejecución: {e}")
"""
if __name__ == "__main__":
        PATH_PLANTILLA = "patron.bmp"
        PATH_ESCENA = "imagen.tif"
        PATH_SALIDA = "imagen_vertices.tif"

        ejecutar_prueba(PATH_PLANTILLA,PATH_ESCENA,PATH_SALIDA)

