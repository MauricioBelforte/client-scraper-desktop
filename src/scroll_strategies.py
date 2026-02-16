import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys




def estrategia_scroll_js_focalizado(driver, parent_element, logger=None):
    """
    QUÉ HACE:
    Ejecuta un scroll rápido manipulando el DOM directamente con JavaScript,
    pero limitado a un contenedor específico.

    CÓMO LO HACE:
    Busca todos los 'div' dentro de 'parent_element'. Si tienen scroll vertical
    (scrollHeight > clientHeight), mueve la barra hasta el final.

    VENTAJA:
    - Velocidad: Es instantáneo.
    - Seguridad: Al recibir un 'parent_element', no afecta al menú lateral ni a otros elementos.
    """
    if logger: logger("Ejecutando Estrategia 1: Scroll JS (Rápido)...")
    
    # Script optimizado para buscar scrollbars solo dentro del padre
    driver.execute_script("""
        var parent = arguments[0];
        var divs = parent.querySelectorAll('div');
        for (var i = 0; i < divs.length; i++) {
            var d = divs[i];
            if (d.scrollHeight > d.clientHeight) {
                d.scrollTop = d.scrollHeight;
            }
        }
    """, parent_element)
    
    time.sleep(1.5) # Breve espera para carga






def estrategia_scroll_teclado(driver, parent_element, logger=None):
    """
    QUÉ HACE:
    Simula pulsaciones físicas de teclas (Page Down) sobre el elemento.

    CÓMO LO HACE:
    1. Hace clic en una esquina neutral del elemento para darle 'foco'.
    2. Envía la tecla PAGE_DOWN varias veces con pausas humanas.

    VENTAJA:
    - Naturalidad: Google Maps detecta esto como un humano real.
    - Efectividad: A menudo activa eventos de carga (lazy load) que JS ignora.
    """
    if logger: logger("Ejecutando Estrategia 2: Scroll Teclado (Humano)...")

    try:
        # 1. Dar foco (Clic en esquina superior izquierda, offset 10,10)
        ActionChains(driver).move_to_element_with_offset(parent_element, 10, 10).click().perform()
        time.sleep(0.5)

        # 2. Pulsar teclas
        for _ in range(3):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(random.uniform(1.0, 1.5))
    except Exception as e:
        if logger: logger(f"⚠️ Falló estrategia teclado: {e}")