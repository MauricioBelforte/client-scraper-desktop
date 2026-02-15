import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


def create_driver(headless=False):
    # Usa la misma carpeta de perfil que `configurar_perfil.py` para mantener el login
    profile_dir = os.path.join(os.getcwd(), "selenium_profile")

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--lang=es-419")
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Minimizar huella
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        })
    except Exception:
        pass
    return driver


def find_scrollable_container(driver, item_selector='div[role="article"]'):
    script = '''
    const sel = arguments[0];
    const item = document.querySelector(sel);
    if (!item) return null;
    let parent = item;
    while (parent && parent !== document.body) {
        const style = window.getComputedStyle(parent);
        const overflowY = style.overflowY;
        if (parent.scrollHeight > parent.clientHeight && (overflowY === 'auto' || overflowY === 'scroll' || parent.scrollTop > 0)) {
            return parent;
        }
        parent = parent.parentElement;
    }
    return null;
    '''
    return driver.execute_script(script, item_selector)


def find_reviews_container(driver):
    script = '''
    var containers = document.querySelectorAll('div.m6QErb.DxyBCb');
    for(var i=0; i<containers.length; i++){
        var c = containers[i];
        var st = window.getComputedStyle(c);
        if((st.overflowY === 'auto' || st.overflowY === 'scroll') && c.scrollHeight > c.clientHeight && c.querySelector('[data-review-id]')){
            return c;
        }
    }
    var allDivs = document.querySelectorAll('div');
    for(var i=0; i<allDivs.length; i++){
        var d = allDivs[i];
        var st = window.getComputedStyle(d);
        var reviews = d.querySelectorAll('[data-review-id]');
        if((st.overflowY === 'auto' || st.overflowY === 'scroll') && d.scrollHeight > d.clientHeight && reviews.length > 0){
            if(!d.parentElement || window.getComputedStyle(d.parentElement).overflowY !== 'auto'){
                return d;
            }
        }
    }
    var r = document.querySelector('[data-review-id]');
    if(r){
        var p = r.parentElement;
        while(p && p !== document.body){
            var st = window.getComputedStyle(p);
            if((st.overflowY === 'auto' || st.overflowY === 'scroll') && p.scrollHeight>p.clientHeight) return p;
            p = p.parentElement;
        }
        return r.parentElement;
    }
    return null;
    '''
    return driver.execute_script(script)


def dispatch_wheel(driver, element, delta_y):
    # Dispara un WheelEvent sobre el elemento para imitar scroll del usuario
    script = ("arguments[0].dispatchEvent(new WheelEvent('wheel', {deltaY: %d, bubbles:true, cancelable:true}));")
    driver.execute_script(script % delta_y, element)


def scroll_reviews(driver, item_selector='div[role="article"]', pause=0.8, max_empty=4):
    # Intentos para localizar el contenedor que realmente controla el scroll
        # Intentar localizar primero el bloque de reseñas (salteando 'Pedir en línea')
        container = find_reviews_container(driver)
        if not container:
            container = find_scrollable_container(driver, item_selector)
    if not container:
        fallbacks = [
            'div[aria-label="Reseñas"]',
            'div[aria-label="Reviews"]',
            '.section-scrollbox',
            'div[role="main"]'
        ]
        for s in fallbacks:
            container = find_scrollable_container(driver, s)
            if container:
                break

    if not container:
        # Intentar abrir el panel de reseñas (botón 'Reseñas' o 'All reviews')
        try:
            btn = driver.find_element(By.XPATH, "//button//span[text()='Reseñas' or text()='Reviews']")
            ActionChains(driver).move_to_element(btn).click().perform()
            time.sleep(1)
            container = find_scrollable_container(driver, item_selector)
        except Exception:
            pass

    if not container:
        raise RuntimeError("No se encontró contenedor scrollable de reseñas; ajusta `item_selector` y abre el panel manualmente.")

    try:
        ActionChains(driver).move_to_element(container).click().perform()
    except Exception:
        pass

    prev_count = 0
    empty_cycles = 0
    while True:
        elems = driver.find_elements(By.CSS_SELECTOR, item_selector)
        count = len(elems)
        if count > prev_count:
            empty_cycles = 0
            prev_count = count
        else:
            empty_cycles += 1
            if empty_cycles >= max_empty:
                break

        # Scroll en el contenedor y simular rueda
        try:
            driver.execute_script("arguments[0].scrollBy({top: arguments[0].clientHeight, behavior:'smooth'});", container)
            dispatch_wheel(driver, container, int(container.size['height']) if hasattr(container, 'size') else 800)
        except Exception:
            # Fallback a scroll del window sobre el elemento visible
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elems[-1] if elems else container)

        time.sleep(pause)

    return driver.find_elements(By.CSS_SELECTOR, item_selector)


def main():
    parser = argparse.ArgumentParser(description='Buscar emprendimiento y recolectar reseñas (pruebas).')
    parser.add_argument('url', help='URL de Google Maps del negocio (abierta en panel lateral)')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--selector', default='div[role="article"]', help='Selector CSS para identificar una reseña')
    args = parser.parse_args()

    driver = create_driver(headless=args.headless)
    try:
        driver.get(args.url)
        time.sleep(2)

        # Espera mínima para que aparezca el panel; el usuario puede necesitar abrir el panel antes
        try:
            reviews = scroll_reviews(driver, item_selector=args.selector)
            print(f"Reseñas encontradas: {len(reviews)}")
        except Exception as e:
            print("Error durante el scroll:", e)
            print("Sugerencia: inspecciona un nodo de reseña y pasa su selector con --selector")

    finally:
        driver.quit()


if __name__ == '__main__':
    main()
