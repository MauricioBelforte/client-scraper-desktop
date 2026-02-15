# 📋 Plan de Refactorización Detallado: client-scraper-desktop

Esta guía desglosa la refactorización de `lead_app.py` en tareas atómicas y específicas. Cada ítem representa una única pieza de lógica que debe ser extraída y modularizada. El objetivo es que cada commit sea pequeño, enfocado y fácil de revisar.

**Estructura de Carpetas Objetivo:**
```
client-scraper-desktop/
├── src/
│   ├── __init__.py
│   ├── constants.py      # (Fase 1)
│   ├── utils.py          # (Fase 2)
│   ├── data_manager.py   # (Fase 3)
│   ├── ui_manager.py     # (Fase 4)
│   └── scraper.py        # (Fase 5)
├── lead_app.py           # (Se convertirá en el orquestador/controlador)
├── ... (otros archivos)
```

---

## Fase 1: Extracción de Constantes y Configuraciones

*Objetivo: Mover todos los valores estáticos (texto, números, configuraciones) a un único lugar para facilitar su modificación.*

- [x] **1. Crear Módulo de Constantes:** Crea la carpeta `src` y dentro el archivo `src/constants.py`.
- [x] **2. Mover `RUBROS_SUGERIDOS`:** Corta la lista `rubros_sugeridos` de `lead_app.py` y pégala en `src/constants.py` como `RUBROS_SUGERIDOS`. Importa y úsala en `setup_ui`.
- [ ] **3. Mover Nombres de Carpetas:** Crea constantes en `src/constants.py` para `"fichas_leads"` y `"selenium_profile"`. Por ejemplo: `DATA_FOLDER = "fichas_leads"`. Reemplaza el texto literal en el código por estas constantes.
- [ ] **4. Mover Colores y Fuentes:** Crea constantes para los códigos de color (`#f8f9fa`, `#1a73e8`, etc.) y las definiciones de fuentes (`("Segoe UI", 10)`) en `src/constants.py`. Reemplaza los valores en el código.
- [ ] **5. Mover Textos de la UI:** Crea constantes para todos los textos fijos de la UI (títulos de ventanas, etiquetas, mensajes de error) en `src/constants.py`.

---

## Fase 2: Extracción de Funciones de Utilidad

*Objetivo: Aislar funciones puras que no dependen del estado de la aplicación (no usan `self`).*

- [ ] **6. Crear Módulo de Utilidades:** Crea el archivo `src/utils.py`.
- [ ] **7. Mover `abrir_whatsapp`:** Mueve el método `abrir_whatsapp` a `src/utils.py` como una función normal (sin `self`). Importa y actualiza la llamada en `mostrar_detalle`.
- [ ] **8. Crear `create_whatsapp_url`:** Dentro de `utils.py`, crea una función `create_whatsapp_url(nombre, tel)` que contenga solo la lógica de limpiar el número y formatear la URL. La función `abrir_whatsapp` ahora llamará a esta y luego a `webbrowser.open()`.

---

## Fase 3: Centralización del Manejo de Datos

*Objetivo: Crear una clase dedicada exclusivamente a leer y escribir archivos en el disco.*

- [ ] **9. Crear Clase `DataManager`:** Crea el archivo `src/data_manager.py` con una clase `DataManager`. Su `__init__` debe recibir el path de la carpeta de datos.
- [ ] **10. Mover Lógica de Guardado:** Mueve la lógica de `open(..., 'w')` y `json.dump()` de `ejecutar_scraping` y `ejecutar_enriquecimiento_masivo` a un método `save_prospects(self, filename, data)` en `DataManager`.
- [ ] **11. Mover Lógica de Carga:** Mueve la lógica de `open(..., 'r')` y `json.load()` de `cargar_ficha_offline` y `start_scraping_thread` a un método `load_prospects(self, filename)` en `DataManager`.
- [ ] **12. Mover Lógica de Listado de Fichas:** Mueve la lógica de `os.listdir()` de `actualizar_lista_fichas` a un método `get_saved_file_names(self)` en `DataManager`.

---

## Fase 4: Aislamiento de la Lógica del Scraper (Selenium)

*Objetivo: Descomponer la monolítica función `ejecutar_scraping` en métodos pequeños y específicos dentro de una nueva clase `Scraper`.*

### 4.1: Configuración y Arranque

- [ ] **13. Crear Clase `Scraper`:** Crea el archivo `src/scraper.py` con una clase `Scraper`. Su `__init__` debe aceptar un `logger_callback` para poder enviar logs a la UI.
- [ ] **14. Mover Configuración de Opciones:** Mueve toda la creación y configuración del objeto `options` de Selenium a un método `_get_chrome_options(self)` en `Scraper`.
- [ ] **15. Mover Inicialización del Driver:** Mueve la creación del `webdriver.Chrome` y la ejecución del comando CDP (`Page.addScriptToEvaluateOnNewDocument`) a un método `_initialize_driver(self)` en `Scraper`.
- [ ] **16. Mover Navegación Inicial:** Mueve la línea `driver.get(...)` a un método `navigate_to_maps(self, driver, query)` en `Scraper`.
- [ ] **17. Mover Espera del Feed:** Mueve la lógica `wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))` a un método `_wait_for_feed(self, wait)` en `Scraper`.

### 4.2: Interacción con la Lista de Resultados

- [ ] **18. Mover Scroll del Feed Principal:** Mueve el primer bucle `for _ in range(4):` que hace scroll en el feed de resultados a un método `_scroll_main_feed(self, driver)` en `Scraper`.
- [ ] **19. Mover Obtención de Locales:** Mueve las líneas `driver.find_elements(...)` que obtienen la lista de `locales` a un método `_get_business_list_elements(self, driver)` en `Scraper`.

### 4.3: Procesamiento de Cada Local (Dentro del Bucle Principal)

- [ ] **20. Mover Extracción de Nombre:** Mueve la lógica para obtener el `nombre` del local a un método `_extract_business_name(self, local_element)` en `Scraper`.
- [ ] **21. Mover Detección de Lead:** Mueve la lógica que busca el botón "Sitio web" y determina si `es_lead` a un método `_is_potential_lead(self, local_element)` en `Scraper`. Este método debe devolver `(True, "SIN WEB 🎯")`, `(True, "SOLO REDES 📱")` o `(False, "")`.
- [ ] **22. Mover Clic y Espera de Detalles:** Mueve el `local.click()` y el `wait.until(...)` para el panel de detalles a un método `_click_and_wait_for_details(self, driver, wait, local_element)` en `Scraper`.

### 4.4: Extracción de Datos del Panel de Detalles

- [ ] **23. Mover Creación de `datos_extra`:** Mueve la inicialización del diccionario `datos_extra` a un método `_initialize_data_dict(self, social_url)` en `Scraper`.
- [ ] **24. Mover Extracción de Teléfono:** Mueve el `try/except` que busca el `tel_element` a un método `_extract_phone(self, driver)` en `Scraper`.
- [ ] **25. Mover Extracción de Dirección:** Mueve el `try/except` que busca la `dir_element` a un método `_extract_address(self, driver)` en `Scraper`.
- [ ] **26. Mover Extracción de Categoría, Rating y Horario:** Agrupa la extracción de estos tres datos simples en un método `_extract_secondary_info(self, driver, data_dict)` en `Scraper`.

### 4.5: Extracción de Reseñas (Sección Compleja)

- [ ] **27. Mover Navegación a Pestaña "Opiniones":** Mueve el `driver.execute_script` que hace clic en la pestaña "Opiniones" a un método `_navigate_to_reviews_tab(self, driver, wait)` en `Scraper`.
- [ ] **28. Mover Scroll de Reseñas (JS):** Mueve el bucle `for i in range(3):` que ejecuta el scroll con JavaScript en el panel de reseñas a un método `_scroll_reviews_panel_js(self, driver)` en `Scraper`.
- [ ] **29. Mover Scroll de Reseñas (Teclado):** Mueve el bloque `try/except` que realiza el scroll con `Keys.PAGE_DOWN` a un método `_scroll_reviews_panel_keyboard(self, driver)` en `Scraper`.
- [ ] **30. Mover Extracción de Datos de Comentarios:** Mueve el bucle `for rev in reviews[:5]:` que extrae autor, texto y rating de cada comentario a un método `_parse_review_elements(self, review_elements)` en `Scraper`.

### 4.6: Extracción Final y Fusión de Datos

- [ ] **31. Mover Navegación a Pestaña "Información":** Mueve el `driver.execute_script` que vuelve a la pestaña "Información" a un método `_navigate_to_overview_tab(self, driver)` en `Scraper`.
- [ ] **32. Mover Scroll Profundo en "Información":** Mueve el bucle de scroll que se ejecuta en la pestaña de información a un método `_scroll_overview_panel(self, driver)` en `Scraper`.
- [ ] **33. Mover Búsqueda de Redes y Email:** Mueve el `find_elements` que busca `facebook.com`, `instagram.com` y `mailto:` a un método `_extract_social_and_email(self, driver)` en `Scraper`.
- [ ] **34. Mover Respaldo de Teléfono (Regex):** Mueve el `try/except` que busca el teléfono con `re.findall` a un método `_extract_phone_fallback(self, driver)` en `Scraper`.
- [ ] **35. Mover Recolección de Imágenes:** Mueve el bucle que recolecta las URLs de `googleusercontent` a un método `_extract_image_urls(self, driver)` en `Scraper`.
- [ ] **36. Mover Lógica de Fusión (Merge):** Mueve el bloque de código de "LÓGICA DE FUSIÓN INTELIGENTE" a un método `merge_data(new_data, old_data)` que podría estar en `DataManager` o `utils.py`.

### 4.7: Aislamiento de Funciones de Búsqueda Externa

- [ ] **37. Mover `buscar_datos_externos`:** Mueve la función completa `buscar_datos_externos` como un método a la clase `Scraper`.
- [ ] **38. Mover `ejecutar_enriquecimiento_masivo`:** Mueve la función completa `ejecutar_enriquecimiento_masivo` como un método `run_bulk_enrichment(self, ...)` a la clase `Scraper`.

---

## Fase 5: Aislamiento de la Interfaz Gráfica (Tkinter)

*Objetivo: Crear una clase que contenga toda la creación y manipulación de widgets de Tkinter.*

- [ ] **39. Crear Clase `UIManager`:** Crea el archivo `src/ui_manager.py` con una clase `UIManager`. Su `__init__` debe recibir el `root` de Tkinter y una referencia al `controller` (la app principal) para conectar los comandos de los botones.
- [ ] **40. Mover `setup_ui`:** Mueve el contenido de `setup_ui` a la clase `UIManager`. Descomponlo en métodos privados para cada sección: `_create_header`, `_create_search_panel`, `_create_main_view`, `_create_status_bar`.
- [ ] **41. Mover `mostrar_detalle`:** Mueve el método `mostrar_detalle` a `UIManager`.
- [ ] **42. Mover `create_info_row`:** Mueve el método `create_info_row` a `UIManager`.
- [ ] **43. Mover `mostrar_info_detallada`:** Mueve el método `mostrar_info_detallada` a `UIManager`.
- [ ] **44. Mover `log`:** Mueve el método `log` a `UIManager`, ya que manipula directamente `self.status_label`.
- [ ] **45. Mover `actualizar_lista_fichas`:** Mueve el método `actualizar_lista_fichas` a `UIManager`, ya que manipula `self.combo_fichas`.
- [ ] **46. Mover Actualizaciones del Treeview:** Centraliza todas las llamadas a `self.tree.insert` y `self.tree.item` en métodos dentro de `UIManager`, como `add_prospect_to_list`, `update_prospect_status`, etc.

---

## Fase 6: Conversión de la Clase Principal a Controlador

*Objetivo: Dejar `lead_app.py` como un archivo pequeño y limpio que solo orquesta las demás clases.*

- [ ] **47. Refactorizar `TrelewLeadApp`:** Una vez que toda la lógica ha sido movida, `TrelewLeadApp` (que podría renombrarse a `AppController`) solo debe:
    - En `__init__`: Instanciar `DataManager`, `UIManager` y `Scraper`.
    - Mantener el estado principal de la aplicación (el diccionario `prospectos_datos`).
    - Contener los métodos que son llamados por los eventos de la UI (ej. `start_scraping_thread`), los cuales a su vez llamarán a los métodos correspondientes en `Scraper` y `DataManager`, y luego usarán `UIManager` para actualizar la vista.

---

### Mensaje para el Commit de este Plan

`docs: Add detailed, step-by-step refactoring plan`