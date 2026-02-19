import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def extraer_fotos_galeria(driver, log_callback=None):
    """
    Estrategia corregida para galería (Overlay):
    1. Usa PAGE_DOWN para scroll (funciona mejor en overlays).
    2. Prioriza el botón 'Atrás' de la UI para no romper la lista de resultados.
    """
    urls_fotos = []
    try:
        if log_callback: log_callback("📸 Abriendo galería...")

        # 1. ABRIR GALERÍA: Identificar si hay pestaña "Fotos" o botón de imagen
        abierto = False
        
        # Intento A: Pestaña "Fotos" (Más seguro)
        try:
            elementos = driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
            for el in elementos:
                txt = el.get_attribute("aria-label") or el.text or ""
                if "Fotos" in txt or "Photos" in txt:
                    driver.execute_script("arguments[0].click();", el)
                    abierto = True
                    time.sleep(2.5)
                    break
        except: pass

        # Intento B: Botón de foto principal (Si no hay pestaña)
        if not abierto:
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Foto'], button[aria-label*='Photo']")
                if btns:
                    driver.execute_script("arguments[0].click();", btns[0])
                    abierto = True
                    time.sleep(2.5)
            except: pass
        
        if not abierto:
            return []

        # 2. EXTRACCIÓN CON SCROLL DE TECLADO (PAGE_DOWN)
        # Esta técnica es más robusta para overlays que el scroll JS
        nuevas_urls = set()
        
        # Hacemos foco en el cuerpo para asegurar que las teclas funcionen
        try: 
            driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)
        except: pass

        for _ in range(5): # 5 intentos de scroll
            # Capturar imágenes visibles
            imgs = driver.find_elements(By.CSS_SELECTOR, "img")
            for img in imgs:
                try:
                    src = img.get_attribute("src")
                    if src and ("googleusercontent" in src or "gstatic" in src):
                        if "s20-c" not in src and "s40-c" not in src and "icon" not in src:
                            nuevas_urls.add(src)
                except: pass
            
            # Scroll con Teclado
            try:
                ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(1.5)
            except: break
        
        urls_fotos = list(nuevas_urls)
        if log_callback: log_callback(f"✅ {len(urls_fotos)} fotos capturadas.")

        # 3. RETORNO SEGURO (CRÍTICO)
        if log_callback: log_callback("↩️ Cerrando galería...")
        
        # Prioridad 1: Botón Atrás de la UI (Flecha arriba a la izquierda)
        # Es vital usar este botón y NO driver.back() para mantener la sesión viva.
        try:
            btn_atras = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Atrás'], button[aria-label='Back']")
            if btn_atras.is_displayed():
                driver.execute_script("arguments[0].click();", btn_atras)
                time.sleep(2)
                return urls_fotos
        except: pass

        # Prioridad 2: Botón Cerrar (X)
        try:
            btn_close = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Cerrar'], button[aria-label='Close']")
            if btn_close.is_displayed():
                driver.execute_script("arguments[0].click();", btn_close)
                time.sleep(2)
                return urls_fotos
        except: pass

        # Prioridad 3: Tecla ESC (Último recurso)
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
        except: pass

    except Exception as e:
        if log_callback: log_callback(f"❌ Error en módulo fotos: {e}")
        # Intento final de escape
        try: ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except: pass

    return urls_fotos
