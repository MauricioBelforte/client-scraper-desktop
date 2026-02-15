import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def prueba_posicionamiento():
    print("🚀 Iniciando prueba de mouse...")
    
    # Configuración básica
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized") # Maximizar para tener referencia clara
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Vamos a una página larga para poder hacer scroll
        print("🌐 Navegando a una página de prueba...")
        driver.get("https://es.wikipedia.org/wiki/Python")
        
        print("⏳ Esperando 10 segundos (Observa la pantalla)...")
        time.sleep(10)
        
        # Obtener dimensiones REALES del área de contenido (Viewport)
        # get_window_size incluye bordes y barras del navegador, lo que causa el error "out of bounds"
        w = driver.execute_script("return window.innerWidth")
        h = driver.execute_script("return window.innerHeight")
        
        # Calcular coordenadas 60% X, 70% Y (Reducido para evitar error OutOfBounds)
        target_x = int(w * 0.60)
        target_y = int(h * 0.70)
        
        print(f"📏 Dimensiones Ventana: {w}x{h}")
        print(f"🎯 Objetivo (60% X, 70% Y): X={target_x}, Y={target_y}")
        
        # --- SOLUCIÓN DEFINITIVA: elementFromPoint ---
        # Preguntamos al navegador qué objeto está en esa coordenada visual y lo operamos directamente.
        # Esto evita el error "MoveTargetOutOfBoundsException".
        target_element = driver.execute_script("return document.elementFromPoint(arguments[0], arguments[1]);", target_x, target_y)
        
        if target_element:
            print(f"✅ Elemento encontrado bajo el mouse: <{target_element.tag_name}>")
            actions = ActionChains(driver)
            actions.move_to_element(target_element).click().perform()
            
            print("🖱️ ¡Haciendo SCROLL ahora!")
            actions.send_keys(Keys.PAGE_DOWN).pause(1).send_keys(Keys.PAGE_DOWN).perform()
            print("✅ Acción completada.")
        else:
            print("⚠️ No se encontró ningún elemento en esas coordenadas.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

    input("🛑 Script pausado. Presiona ENTER para finalizar y cerrar el navegador...")
    driver.quit()

if __name__ == "__main__":
    prueba_posicionamiento()