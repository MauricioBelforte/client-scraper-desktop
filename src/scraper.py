# src/scraper.py

from selenium import webdriver  # import aquí para facilitar monkeypatch en tests
from webdriver_manager.chrome import ChromeDriverManager  # import en el top level para facilitar mocking en tests

class Scraper:
    """Clase que encapsulará toda la lógica de scraping con Selenium.

    El constructor recibe un callback de logging para comunicar mensajes a la UI.
    """
    def __init__(self, logger_callback=None):
        self.logger = logger_callback

    def _log(self, mensaje):
        if self.logger:
            self.logger(mensaje)

    def _get_chrome_options(self):
        """Construye y devuelve un objeto `Options` configurado con todas las
        banderas anti-detección y optimizaciones que usaba previamente el
        método monolítico `ejecutar_scraping` en `lead_app.py`.
        """
        from selenium.webdriver.chrome.options import Options
        import os
        import src.constants as constantes

        options = Options()
        options.add_argument("--lang=es-419")  # Forzar español latino
        # --- MEDIDAS ANTI-DETECCIÓN (STEALTH) ---
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        # --- OPTIMIZACIÓN DE RECURSOS ---
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        # --- PERFIL PERSISTENTE ---
        profile_dir = os.path.join(os.getcwd(), constantes.CARPETA_PERFIL)
        options.add_argument(f"--user-data-dir={profile_dir}")
        return options

    def _initialize_driver(self):
        """Crea y devuelve una instancia de `webdriver.Chrome` usando las
        opciones construidas por `_get_chrome_options`.
        """

        from selenium.webdriver.chrome.service import Service

        options = self._get_chrome_options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # inyección anti-detección CDP script podría añadirse aquí en el futuro
        return driver

    def navigate_to_maps(self, driver, query: str):
        """Navega a la búsqueda de Google Maps para el rubro especificado."""
        base = "https://www.google.com/maps/search/"
        # reemplazar espacios por + para la URL
        url = base + query.replace(' ', '+')
        driver.get(url)

    def _wait_for_feed(self, wait):
        """Espera hasta que el contenedor de resultados aparezca en la página.

        Parámetro `wait` puede ser cualquier objeto con método `until` (facilita
        testing con mocks).
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC

        return wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
