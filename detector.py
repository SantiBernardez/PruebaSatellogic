import cv2
import numpy as np

#NOTA IMPORTANTE: No hay cortex a59, o se equivocaron o lo hicieron aproposito a ver si alguien decia algo, hay A53, A55 y A57 pero no A59.
#De todas formas voy a asumir que se refieren a un procesador de baja potencia.
#Nota explicativa: Uso un algoritmo generico para encontrar semicirculo, ya que me piden que como argumento patron.bmp, y luego dentro del patron encuentro los vertices. En un principio habia pensado en usar algun metodo especifico, que capaz sea mas eficiente, pero como dije, se supone debe de buscar una imagen generica (para hacermela facil asumo que es blanco y negro ya que eso ponia la letra)


 
#Me voy a referir a los vertices asi: C es el vertice que forma el angulo recto, mientras que A y B son los otros 2, es decir, aquellos que crucan circunferencia con corte.
# Ya que dijieron que el fondo es principalmente negro y que es un procesador de poca potencia asumo que solo el threshold ya alcanza para limpiar ruido. Si no me dan mas ejemplos no puedo hacer mucho, sorry.

def buscar_vertices_en_escena(path_plantilla, path_escena, benchmark=False):
    if benchmark: # Solo sirve para medir tiempo.
        import time
        t_inicio_total = time.perf_counter()
        t_inicio_disco = time.perf_counter()
        
    # CARGA DE AMBAS IMÁGENES
    img_template = cv2.imread(path_plantilla, cv2.IMREAD_GRAYSCALE)
    img_scene = cv2.imread(path_escena, cv2.IMREAD_GRAYSCALE)
    
    if benchmark:
        t_total_disco = time.perf_counter() - t_inicio_disco

    if img_template is None or img_scene is None:
        raise FileNotFoundError("Verificá los paths de las imágenes.")

    # =========================================================================
    # INICIO DE MEDICIÓN EXCLUSIVA: LOCALIZACIÓN DE LA ESCENA
    # =========================================================================
    if benchmark:
        t_inicio_localizacion = time.perf_counter()

    h_orig, w_orig = img_scene.shape
    FACTOR_REDUCCION = 0.05  
    INV_FACTOR = 20.0

    # PRE-PROCESAMIENTO DE LA PLANTILLA EN ESCALA BAJA
    img_tmp_small = cv2.resize(img_template, (0, 0), fx=FACTOR_REDUCCION, fy=FACTOR_REDUCCION, interpolation=cv2.INTER_NEAREST)
    _, thresh_tmp_small = cv2.threshold(img_tmp_small, 127, 255, cv2.THRESH_BINARY)
    contours_tmp_small, _ = cv2.findContours(thresh_tmp_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours_tmp_small:
        return False,None,None,None
    
    cnt_template_small = max(contours_tmp_small, key=cv2.contourArea)
    _, _, w_t_ref, h_t_ref = cv2.boundingRect(cnt_template_small)

    # LOCALIZACIÓN EN ESCALA BAJA (Coarse Match con descarte de zonas vacías)
    img_small = cv2.resize(img_scene, (0, 0), fx=FACTOR_REDUCCION, fy=FACTOR_REDUCCION, interpolation=cv2.INTER_NEAREST)
    _, thresh_small = cv2.threshold(img_small, 127, 255, cv2.THRESH_BINARY)
    contours_small, _ = cv2.findContours(thresh_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours_small:
        return False,-1,-1,-1
        
    mejor_match_valor = float('inf')
    cnt_ganador_small = None

    for cnt in contours_small:
        _, _, w_s, h_s = cv2.boundingRect(cnt)
        
        # Filtro geométrico rápido basado en dimensiones aproximadas
        if w_s < (w_t_ref * 0.3) or h_s < (h_t_ref * 0.3) or w_s > (w_t_ref * 3.0):
            continue 
            
        resultado_match = cv2.matchShapes(cnt_template_small, cnt, cv2.CONTOURS_MATCH_I1, 0.0)
        if resultado_match < mejor_match_valor:
            mejor_match_valor = resultado_match
            cnt_ganador_small = cnt

    if cnt_ganador_small is None:
        cnt_ganador_small = max(contours_small, key=cv2.contourArea)

    x_s, y_s, w_s, h_s = cv2.boundingRect(cnt_ganador_small)

    # Escalado de la zona de interés (ROI) con margen de seguridad (PADD)
    PADD = 100
    x_min = max(0, int(x_s * INV_FACTOR) - PADD)
    y_min = max(0, int(y_s * INV_FACTOR) - PADD)
    x_max = min(w_orig, int((x_s + w_s) * INV_FACTOR) + PADD)
    y_max = min(h_orig, int((y_s + h_s) * INV_FACTOR) + PADD)

    # EXTRACCIÓN DE VÉRTICES DE ALTA PRECISIÓN (Fine Match)
    img_roi = img_scene[y_min:y_max, x_min:x_max]
    
    _, thresh_scn_roi = cv2.threshold(img_roi, 127, 255, cv2.THRESH_BINARY)
    contours_scn_roi, _ = cv2.findContours(thresh_scn_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours_scn_roi:
        return False, float('inf'), float('inf'), float('inf')
        
    cnt_elegido = max(contours_scn_roi, key=cv2.contourArea)

    epsilon = 0.005 * cv2.arcLength(cnt_elegido, True)
    poly_approx = cv2.approxPolyDP(cnt_elegido, epsilon, True)
    pts_locales = poly_approx.reshape(-1, 2).astype(np.float32)
    
    # Lógica de distancias máximas para hallar A y B
    diff = pts_locales[:, np.newaxis, :] - pts_locales[np.newaxis, :, :]
    dist_matrix = np.sum(diff ** 2, axis=-1)
    
    idx_A, idx_B = np.unravel_index(np.argmax(dist_matrix), dist_matrix.shape)
    pt_A_local = pts_locales[idx_A]
    pt_B_local = pts_locales[idx_B]

    vec_AB = pt_B_local - pt_A_local
    vec_all_AC = pts_locales - pt_A_local
    
    # Buscamos punto C a maxima distancia de AB
    # El paralelogramo formado por AB y AC tiene area base*altura=AB*AC*sin(\theta), donde \theta es el angulo entre AC y la perpendicular de AB.
    # Lo cual es igual al producto cruz
    # Como base es AB que es cte, el punto que maximiza area es el qeu maximiza altura (distancia entre C y AB).


    # Fórmula del producto cruzado 2D: |(AB_x * AC_y) - (AB_y * AC_x)|
    cross_products = np.abs(vec_AB[0] * vec_all_AC[:, 1] - vec_AB[1] * vec_all_AC[:, 0])
    pt_C_local = pts_locales[np.argmax(cross_products)]

    # TRASLACIÓN DE COORDENADAS LOCALES A GLOBALES
    desfase_global = np.array([x_min, y_min], dtype=np.float32)
    pt_A_exacto = pt_A_local + desfase_global
    pt_B_exacto = pt_B_local + desfase_global
    pt_C_exacto = pt_C_local + desfase_global

    # =========================================================================
    # FIN DE MEDICIÓN EXCLUSIVA: LOCALIZACIÓN DE LA ESCENA
    # =========================================================================
    if benchmark:
        t_final_total = time.perf_counter()
        t_total_localizacion = t_final_total - t_inicio_localizacion
        t_total_funcion = t_final_total - t_inicio_total
        
        print(f"\n[BENCHMARK RENDIMIENTO]")
        print(f" Tiempo I/O (Lectura de Disco): {t_total_disco * 1000:.2f} ms")
        print(f" Tiempo NETO Localización:      {t_total_localizacion * 1000:.2f} ms")
        print(f" Tiempo TOTAL de la Función:    {t_total_funcion * 1000:.2f} ms")

    return True,pt_A_exacto, pt_B_exacto, pt_C_exacto

