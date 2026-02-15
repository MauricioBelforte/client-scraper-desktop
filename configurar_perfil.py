import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def configurar_perfil():
    print("🔧 Abriendo navegador para configuración manual...")
    print("⚠️ RECOMENDACIÓN: Inicia sesión con una cuenta SECUNDARIA (no la personal).")
    
    options = Options()
    options.add_argument("--lang=es-419")
    options.add_argument("--start-maximized")
    
    # --- MEDIDAS ANTI-DETECCIÓN PARA LOGIN ---
    # Necesarias para que Google permita el inicio de sesión sin bloquear
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Usar EXACTAMENTE la misma carpeta de perfil que la app principal
    # Esto permite que lo que hagas aquí (login) se guarde para el robot
    profile_dir = os.path.join(os.getcwd(), "selenium_profile")
    options.add_argument(f"--user-data-dir={profile_dir}")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # --- OCULTAR HUELLA DE ROBOT (CDP) ---
    # Esto evita el mensaje "Navegador no seguro" inyectando código antes de cargar la página
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """
    })
    
    driver.get("https://accounts.google.com/signin")
    
    print("\n✅ Navegador abierto.")
    print("1. Inicia sesión con tu cuenta 'bot' o secundaria.")
    print("2. Ve a Google Maps y acepta cookies si te lo pide.")
    print("3. Cuando termines, cierra el navegador manualmente.")
    
    input("\nPresiona ENTER en esta consola cuando hayas cerrado el navegador...")
    driver.quit()

if __name__ == "__main__":
    configurar_perfil()