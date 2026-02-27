# 📋 Plan de Refactorización Detallado: client-scraper-desktop

> **Nota:** Las normas de estilo y commits se encuentran en `AGENTS.md`.
 
Esta guía desglosa la refactorización de `lead_app.py` en tareas atómicas y específicas. Cada ítem representa una única pieza de lógica que debe ser extraída y modularizada. El objetivo es que cada commit sea pequeño, enfocado y fácil de revisar.

**Estructura de Carpetas Objetivo:**
```
client-scraper-desktop/
├── src/
│   ├── __init__.py
│   ├── constants.py      # (Fase 1)
│   ├── utilidades.py     # (Fase 2)
│   ├── gestor_datos.py   # (Fase 3)
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
- [x] **3. Mover Nombres de Carpetas:** Crea constantes en `src/constants.py` para `"fichas_leads"` y `"selenium_profile"`. Por ejemplo: `DATA_FOLDER = "fichas_leads"`. Reemplaza el texto literal en el código por estas constantes.
- [x] **4. Mover Colores y Fuentes:** Crea constantes para los códigos de color (`#f8f9fa`, `#1a73e8`, etc.) y las definiciones de fuentes (`("Segoe UI", 10)`) en `src/constants.py`. Reemplaza los valores en el código.
- [x] **5. Mover Textos de la UI (OPCIONAL):** Inicialmente se colocaron como constantes. Se revisará cada texto; si se usa en más de un lugar o cambia dinámicamente, mantenerlo aquí; de lo contrario, volverlo literal en el código para mejorar legibilidad y eliminarlo de `constants.py`. Esta decisión se refleja en la fase de limpieza posterior.

---

## Fase 2: Extracción de Funciones de Utilidad

*Objetivo: Aislar funciones puras que no dependen del estado de la aplicación (no usan `self`).*

- [x] **6. Crear Módulo de Utilidades:** Crea el archivo `src/utilidades.py`.
- [x] **7. Mover `abrir_whatsapp`:** Mueve el método `abrir_whatsapp` a `src/utilidades.py` como una función normal (sin `self`). Importa y actualiza la llamada en `mostrar_detalle`.
- [x] **8. Crear `create_whatsapp_url`:** Dentro de `utilidades.py`, crea una función `create_whatsapp_url(nombre, tel)` que contenga solo la lógica de limpiar el número y formatear la URL. La función `abrir_whatsapp` ahora llamará a esta y luego a `webbrowser.open()`.

---

## Fase 3: Centralización del Manejo de Datos

*Objetivo: Crear una clase dedicada exclusivamente a leer y escribir archivos en el disco.*

- [x] **9. Crear Clase `GestorDatos`:** Crea el archivo `src/gestor_datos.py` con una clase `GestorDatos`. Su `__init__` debe recibir el path de la carpeta de datos.
- [x] **10. Mover Lógica de Guardado:** Mueve la lógica de `open(..., 'w')` y `json.dump()` de `ejecutar_scraping` y `ejecutar_enriquecimiento_masivo` a un método `guardar_datos(self, nombre_archivo, datos)` en `GestorDatos`.
- [x] **11. Mover Lógica de Carga:** Mueve la lógica de `open(..., 'r')` y `json.load()` de `cargar_ficha_offline` y `start_scraping_thread` a un método `cargar_datos(self, nombre_archivo)` en `GestorDatos`.
- [x] **12. Mover Lógica de Listado de Fichas:** Mueve la lógica de `os.listdir()` de `actualizar_lista_fichas` a un método `obtener_archivos(self)` en `GestorDatos`.

---

## Fase 4: Aislamiento de la Lógica del Scraper (Selenium)

*Objetivo: Descomponer la monolítica función `ejecutar_scraping` en métodos pequeños y específicos dentro de una nueva clase `Scraper`.*

> **Nota actual:** ya existen módulos auxiliares `src/scroll_strategies.py` (estrategias de scroll) y `src/enriquecedor.py` (búsqueda externa global). La fase considera cómo integrar o migrar esas piezas dentro de `Scraper` según convenga.

### 4.1: Configuración y Arranque

- [x] **13. Crear Clase `Scraper`:** Crea el archivo `src/scraper.py` con una clase `Scraper`. Su `__init__` debe aceptar un `logger_callback` para poder enviar logs a la UI. (Realizado, clase es instanciable y test asociado creado)
- [x] **14. Mover Configuración de Opciones:** Mueve toda la creación y configuración del objeto `options` de Selenium a un método `_get_chrome_options(self)` en `Scraper`. (Implementado y verificado mediante prueba 4_1_14)
- [x] **15. Mover Inicialización del Driver:** Mueve la creación del `webdriver.Chrome` y la ejecución del comando CDP (`Page.addScriptToEvaluateOnNewDocument`) a un método `_initialize_driver(self)` en `Scraper`. (Implementado y cubierto por test 4_1_15)
- [x] **16. Mover Navegación Inicial:** Mueve la línea `driver.get(...)` a un método `navigate_to_maps(self, driver, query)` en `Scraper`. (Implementado y verificado con test 4_1_16)
- [x] **17. Mover Espera del Feed:** Mueve la lógica `wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))` a un método `_wait_for_feed(self, wait)` en `Scraper`. (Hecho y cubierto con test 4_1_17)

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
    - En `__init__`: Instanciar `GestorDatos`, `UIManager` y `Scraper`.
    - Mantener el estado principal de la aplicación (el diccionario `prospectos_datos`).
    - Contener los métodos que son llamados por los eventos de la UI (ej. `start_scraping_thread`), los cuales a su vez llamarán a los métodos correspondientes en `Scraper` y `GestorDatos`, y luego usarán `UIManager` para actualizar la vista.

---

## Fase 7: Cobertura de Tests y Calidad

*Objetivo: Asegurar que cada unidad de código tenga pruebas automatizadas y configurar la integración continua.*

- [ ] **48. Crear estructura de pruebas:** Añadir la carpeta `test/` con un `__init__.py` y un subdirectorio `test/refactorizacion/` donde irán todas las pruebas específicas de refactorización. Dentro de esta carpeta pueden crearse subcarpetas por fase (ej. `fase 4-1-configuracion-arranque`). Los archivos deben numerarse secuencialmente (`1_test_xyz.py`, `2_test_abc.py`, etc.) para facilitar ordenamiento.- [ ] **49. Tests para utilidades y constantes:** En `test/refactorizacion/` escribe pruebas unitarias que verifiquen valores de constantes y el comportamiento de `create_whatsapp_url`, etc.
- [ ] **50. Tests para `GestorDatos`:** En el mismo subdirectorio, simular lectura/escritura usando `tmp_path` y validar métodos `guardar_datos`, `cargar_datos` y `obtener_archivos`.
- [ ] **51. Tests para `Scraper` con mocking:** Usar `unittest.mock` para comprobar que cada método aislado es invocado correctamente sin abrir un navegador real.
- [ ] **52. Tests para `UIManager`:** Crear pruebas que instancien la clase en un root de Tkinter y simulen eventos básicos; verificar que los widgets se crean y actualizan.
- [ ] **53. Configurar CI:** Añadir un workflow de GitHub Actions (`.github/workflows/tests.yml`) que instale dependencias y ejecute `pytest` en cada push/pull request.

---

## Fase 8: Revisión Final y Preparación de Release

*Objetivo: Pulir detalles, documentar cambios y dejar el repositorio listo para un tag/versión.*

- [ ] **54. Limpieza de imports y código muerto:** Ejecutar `flake8`/`ruff` y eliminar funciones o variables sin uso. Aprovechar para borrar constantes de texto de UI que ya fueron movidas a literales o que no se utilizan.
- [ ] **55. Actualizar documentación:** Revisar `README.md`, `AGENTS.md` y los archivos en `documentacion/` para reflejar la nueva arquitectura.
- [ ] **56. Verificación de estilo:** Correr pre‑commit hooks y confirmar que no quedan advertencias de formato o lint.
- [ ] **57. Generar notas de release:** Redactar un `CHANGELOG.md` o sección en el README con los cambios importantes de la refactorización.
- [ ] **58. Crear rama de release y etiqueta:** Preparar branch `release/vX.Y` y aplicar un tag semántico cuando todo esté aprobado.

---

## 🐛 Problemas Identificados y Corregidos

### BUG #001: Ventana de Ficha Técnica Aparecía Vacía

**Estado:** ✅ CORREGIDO  
**Fecha:** 27 de febrero de 2026  
**Severidad:** Medio (funcionalidad visual)  

**Descripción:**
Cuando el usuario presionaba el botón "VER FICHA TÉCNICA" en la tarjeta de detalles, se abría una ventana emergente pero aparecía completamente vacía, sin mostrar la información recopilada del emprendimiento.

**Causa Raíz:**
Durante la refactorización de Fase 1 (Extracción de Constantes), se removieron del archivo `src/constants.py` cuatro constantes de texto que se usaban en la función `mostrar_info_detallada()`:
- `ENCABEZADO_FICHA` → Encabezado de la ventana de ficha técnica
- `SECCION_COMENTARIOS` → Etiqueta de la sección de comentarios
- `MSJ_SIN_COMENTARIOS` → Mensaje cuando no hay comentarios
- `NOTA_PIE` → Texto de advertencia al pie

Sin embargo, estas constantes seguían siendo referenciadas en `lead_app.py` (líneas 438, 836, 890, 900, 903). Cuando Tkinter intentaba acceder a ellas, se levantaba un `AttributeError`, lo que causaba que los labels se crearan vacíos.

**Síntomas:**
- La ventana se abría sin problemas
- Los frames y estructura estaban presente
- Los labels aparecían vacíos en lugar de mostrar el texto esperado
- No se levantaba un error visible al usuario

**Solución Aplicada:**
Reemplazar todas las referencias a constantes faltantes con literales en español:

| Variable Constante | Línea | Reemplazada por |
|-------------------|-------|-----------------|
| `COLUMNA_NOMBRE` | 140 | `"Nombre"` |
| `COLUMNA_ESTADO` | 141 | `"Estado"` |
| `ENCABEZADO_CARD` | 371 | `"Información del Emprendimiento"` |
| `TEXTO_PLACEHOLDER_CARD` | 212 | `"Selecciona un emprendimiento para ver detalles"` |
| `ESTADO_LISTO` | 220 | `"Listo"` |
| `ENCABEZADO_FICHA` | 836 | `"Información Pública del Emprendimiento"` |
| `SECCION_COMENTARIOS` | 890 | `"Comentarios y Reseñas"` |
| `MSJ_SIN_COMENTARIOS` | 900 | `"No hay comentarios disponibles"` |
| `NOTA_PIE` | 903 | `"Esta información fue recopilada automáticamente desde Google Maps y sitios web públicos. Verifica los datos directamente con el emprendimiento."` |

Además, se actualizó el texto del botón:
- **Antes:** `"📄 VER FICHA TÉCNICA (WEB DEMO)"`
- **Después:** `"📄 VER FICHA TÉCNICA"`

**Tests Asociados:**
Se creó el archivo `test/refactorizacion/4_test_ficha_tecnica.py` con tres tests:
1. `test_mostrar_info_detallada_no_falla()` → Verifica que la función se ejecute sin errores
2. `test_botón_ficha_tecnica_texto_actualizado()` → Valida que "(WEB DEMO)" fue removido
3. `test_no_referencias_a_constantes_faltantes()` → Confirma que no existan referencias a constantes removidas

**Lecciones Aprendidas:**
1. **Verificación cruzada:** Cuando se remuevan constantes, realizar una búsqueda exhaustiva en todo el codebase para asegurar que no hay referencias huérfanas.
2. **Tests preventivos:** Los tests de regresión como `test_no_referencias_a_constantes_faltantes()` podrían haber detectado este problema preemptivamente.
3. **Documentación de cambios:** Mantener un registro de qué constantes se removieron y por qué, especialmente durante refactorizaciones.

---

### Mensaje para el Commit de este Plan

`docs: Add detailed, step-by-step refactoring plan`