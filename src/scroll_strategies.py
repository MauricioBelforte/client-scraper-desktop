import time
import random

def ejecutar_scroll_agresivo(driver, logger=None):
    """
    Estrategia de scroll agresiva que busca todos los divs con scroll y los baja.
    NOTA: Puede afectar el feed principal si no se tiene cuidado.
    """
    if logger:
        logger("Iniciando scroll agresivo (Estrategia Legacy)...")

    for i in range(3): # Realizar 3 ciclos de scroll/carga
        # Hacemos scroll para pedir más contenido
        driver.execute_script("""
            var divs = document.querySelectorAll('div');
            for (var j = 0; j < divs.length; j++) {
                var s = window.getComputedStyle(divs[j]);
                if ((s.overflowY === 'auto' || s.overflowY === 'scroll') && divs[j].scrollHeight > divs[j].clientHeight) {
                    if (divs[j].clientHeight > 100) {
                        divs[j].scrollTop = divs[j].scrollHeight;
                        divs[j].dispatchEvent(new WheelEvent('wheel', { deltaY: 1000, bubbles: true }));
                    }
                }
            }
        """)
        
        # Espera simple para carga de reseñas sin minimizar
        if logger:
            logger(f"Cargando reseñas (ciclo {i+1}/3)...")
        time.sleep(random.uniform(2, 4))
        time.sleep(1) # Pequeña pausa para que se redibuje