# 📋 Plan de Refactorización y Modularización: client-scraper-desktop

Esta guía detalla el proceso paso a paso para refactorizar la aplicación `lead_app.py` en una estructura de código modular, limpia y escalable. Cada ítem es una tarea independiente que debe completarse en orden.

## Fase 1: Constantes y Configuraciones

El objetivo es extraer valores estáticos que no cambian.

- [ ] **1.1: Crear módulo de constantes (`src/constants.py`)**
    - **Acción:** Crea una carpeta `src` en la raíz del proyecto. Dentro, crea un archivo `constants.py`.
    - **Contenido a mover:** Mueve la lista `rubros_sugeridos` desde `lead_app.py` al nuevo archivo.
    - **`src/constants.py` debería contener:**
      ```python
      RUBROS_SUGERIDOS = [
          "Gimnasios", "Restaurantes", "Talleres Mecánicos", "Peluquerías", 
          "Odontólogos", "Abogados", "Inmobiliarias", "Cervecerías", 
          # ... (lista completa)
      ]
      ```
    - **Refactorización en `lead_app.py`:** Importa la constante y úsala en `setup_ui`.
      ```python
      from src.constants import RUBROS_SUGERIDOS
      # ...
      self.entry_rubro = ttk.Combobox(search_frame, values=RUBROS_SUGERIDOS, width=28)
      ```

## Fase 2: Utilidades Generales

Funciones puras que no dependen del estado de la aplicación (`self`).

- [ ] **2.1: Crear módulo de utilidades (`src/utils.py`)**
    - **Acción:** Dentro de la carpeta `src`, crea un archivo `utils.py`.
    - **Contenido a mover:** Mueve la función `abrir_whatsapp` de `lead_app.py` a `utils.py`. La función ya no será un método de la clase.
    - **`src/utils.py` debería contener:**
      ```python
      import webbrowser
      from tkinter import messagebox

      def abrir_whatsapp(nombre, tel):
          # ... (toda la lógica de la función original)
      ```
    - **Refactorización en `lead_app.py`:** Importa la función y actualiza la llamada en `mostrar_detalle`.
      ```python
      from src.utils import abrir_whatsapp
      # ...
      # Dentro de mostrar_detalle:
      tk.Button(..., command=lambda: abrir_whatsapp(nombre, tel) if has_wa else None)
      ```

## Fase 3: Gestión de Datos (Archivos)

Centralizar toda la lectura y escritura de archivos JSON.

- [ ] **3.1: Crear gestor de datos (`src/data_manager.py`)**
    - **Acción:** Crea el archivo `src/data_manager.py`.
    - **Diseño:** Crea una clase `DataManager` que manejará los archivos.
    - **`src/data_manager.py` debería contener:**
      ```python
      import json
      import os

      class DataManager:
          def __init__(self, data_folder="fichas_leads"):
              self.data_folder = data_folder
              if not os.path.exists(self.data_folder):
                  os.makedirs(self.data_folder)

          def save_data(self, filename, data):
              # Lógica para guardar el diccionario 'data' en un archivo JSON llamado 'filename'.json

          def load_data(self, filename):
              # Lógica para cargar un archivo JSON y devolver un diccionario. Si no existe, devuelve {}.

          def get_saved_files(self):
              # Lógica que lee la carpeta y devuelve una lista de nombres de archivo sin la extensión.
      ```
    - **Refactorización en `lead_app.py`:**
        - En `__init__`, instancia `self.data_manager = DataManager()`.
        - Reemplaza la lógica de `open()` y `json.dump()` en `ejecutar_scraping`, `ejecutar_enriquecimiento_masivo`, etc., por una llamada a `self.data_manager.save_data(rubro, self.prospectos_datos)`.
        - Reemplaza la lógica de carga en `start_scraping_thread` y `cargar_ficha_offline` por `self.data_manager.load_data(rubro)`.
        - Reemplaza la lógica de `actualizar_lista_fichas` por `self.data_manager.get_saved_files()`.

## Fase 4: Aislamiento del Scraper (Selenium)

Esta es la fase más compleja. El objetivo es que `lead_app.py` no sepa nada sobre Selenium.

- [ ] **4.1: Crear clase Scraper (`src/scraper.py`)**
    - **Acción:** Crea el archivo `src/scraper.py`.
    - **Diseño:** Crea una clase `Scraper`. El `__init__` puede aceptar un `logger_callback` para enviar mensajes a la UI.
    - **Contenido a mover:**
        1.  **Configuración del Driver:** Mueve toda la lógica de `Options` y `webdriver.Chrome(...)` a un método privado `_setup_driver()`.
        2.  **`buscar_datos_externos`:** Mueve esta función a un método de la clase `Scraper`.
        3.  **`ejecutar_scraping`:** Mueve toda la lógica a un método `run_scraping(self, rubro)`. Este método debe aceptar el `rubro` y los datos previos. Devolverá el diccionario de datos actualizado. La comunicación con la UI (logs, actualización de Treeview) se hará a través de callbacks.
        4.  **`ejecutar_enriquecimiento_masivo`:** Mueve la lógica a un método `run_bulk_enrichment(self, prospectos)`.
    - **Refactorización en `lead_app.py`:**
        - En `__init__`, instancia `self.scraper = Scraper(logger_callback=self.log)`.
        - El método `start_scraping_thread` ahora solo preparará los datos y llamará a un método del scraper en un hilo. Ejemplo: `threading.Thread(target=self.scraper.run_scraping, ...)`.
        - La clase `TrelewLeadApp` ya no tendrá ninguna importación de `selenium`.

## Fase 5: Aislamiento de la Interfaz Gráfica (Tkinter)

- [ ] **5.1: Crear clase de UI (`src/ui_manager.py`)**
    - **Acción:** Crea el archivo `src/ui_manager.py`.
    - **Diseño:** Crea una clase `UIManager`. El `__init__` recibirá el `root` de Tkinter y una referencia a la app principal para conectar los comandos de los botones.
    - **Contenido a mover:**
        1.  **`setup_ui`:** Mueve toda la construcción de la ventana a esta clase.
        2.  **`mostrar_detalle`:** Mueve la lógica de creación de la card de detalle.
        3.  **`mostrar_info_detallada`:** Mueve la lógica de la ventana emergente de ficha técnica.
        4.  **`log` y `actualizar_lista_fichas`:** Mueve los métodos que manipulan directamente widgets de la UI.
    - **Refactorización en `lead_app.py`:**
        - En `__init__`, la clase principal ahora solo hará: `self.ui = UIManager(self.root, self)`. El `self` final es para que la UI pueda llamar a métodos como `start_scraping_thread`.

## Fase 6: Limpieza de la Clase Principal

- [ ] **6.1: Refactorizar `TrelewLeadApp` para que sea un Controlador**
    - **Acción:** Una vez movido todo, `lead_app.py` debe ser muy pequeño.
    - **Responsabilidades:**
        - Orquestar la creación de los managers (`UIManager`, `DataManager`, `Scraper`).
        - Mantener el estado de la aplicación (el diccionario `self.prospectos_datos`).
        - Contener los métodos que son llamados por los botones de la UI (ej: `start_scraping_thread`), los cuales a su vez delegan la lógica pesada a los otros módulos.