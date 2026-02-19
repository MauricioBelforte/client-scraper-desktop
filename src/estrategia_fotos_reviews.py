import re
from selenium.webdriver.common.by import By

def limpiar_url_imagen(url):
    """
    Intenta obtener la versión de alta resolución de la imagen de Google.
    Las URLs suelen tener parámetros como '=w100-h100-p-k-no' o '=s400'.
    Al cambiarlos por '=s0', Google suele devolver la imagen original.
    """
    if not url: return None
    
    # Si es una URL de contenido de usuario de Google
    if "googleusercontent" in url:
        # Reemplazar cualquier parámetro al final por =s0 (tamaño original)
        # Ej: .../photo.jpg?sz=100 -> .../photo.jpg=s0
        # Ej: .../photo.jpg=w200-h200 -> .../photo.jpg=s0
        return re.sub(r'(=s\d+.*|=w\d+.*|=h\d+.*|\?sz=\d+)', '=s0', url)
    
    return url

def extraer_fotos_de_resena(review_element, logger=None):
    """
    Intenta extraer URLs de imágenes adjuntas a una reseña específica.
    Prueba múltiples estrategias sin romper el flujo.
    
    Args:
        review_element (WebElement): El elemento DOM de la reseña individual.
        logger (function, optional): Función para registrar logs.
        
    Returns:
        list: Lista de URLs de imágenes encontradas.
    """
    imagenes = set() # Usamos set para evitar duplicados automáticamente

    # --- ESTRATEGIA 1: Botones con background-image (Vista estándar) ---
    # Google Maps suele poner las fotos como fondo de botones pequeños.
    try:
        btns = review_element.find_elements(By.CSS_SELECTOR, "button[style*='background-image']")
        for btn in btns:
            style = btn.get_attribute("style")
            # Regex para extraer url(...)
            match = re.search(r'url\("?(.+?)"?\)', style)
            if match:
                url = match.group(1)
                url_hq = limpiar_url_imagen(url)
                if url_hq:
                    imagenes.add(url_hq)
    except Exception: pass

    # --- ESTRATEGIA 2: Etiquetas IMG directas (Vista móvil o variantes) ---
    # A veces, dependiendo de la resolución o versión de Maps, son etiquetas <img>.
    if not imagenes:
        try:
            imgs = review_element.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                src = img.get_attribute("src")
                # Filtrar avatares (suelen ser pequeños o tener 'p-k-no' o 's40', 's32')
                # Las fotos de reseñas suelen tener tamaños mayores o IDs largos.
                if src and "googleusercontent" in src and "p-k-no" not in src:
                    # Verificación simple de tamaño (si es posible obtenerlo sin error)
                    try:
                        size = img.size
                        if size['width'] > 60 and size['height'] > 60: # Umbral para descartar iconos
                            url_hq = limpiar_url_imagen(src)
                            if url_hq:
                                imagenes.add(url_hq)
                    except:
                        # Si falla obtener tamaño, agregamos por si acaso (mejor tener basura que perder foto)
                        url_hq = limpiar_url_imagen(src)
                        if url_hq:
                            imagenes.add(url_hq)
        except Exception: pass

    # --- ESTRATEGIA 3: Clases específicas (Ofuscadas) ---
    # A veces Google usa clases como 'Tya61d' para contenedores de fotos.
    if not imagenes:
        try:
            divs_fotos = review_element.find_elements(By.CSS_SELECTOR, ".Tya61d")
            for div in divs_fotos:
                style = div.get_attribute("style")
                match = re.search(r'url\("?(.+?)"?\)', style)
                if match:
                    url = match.group(1)
                    url_hq = limpiar_url_imagen(url)
                    if url_hq:
                        imagenes.add(url_hq)
        except Exception: pass

    return list(imagenes)
