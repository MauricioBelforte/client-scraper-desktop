# 🚀 Hoja de Ruta y Mejoras Sugeridas - Trelew Lead Prospector

Este documento detalla posibles optimizaciones para la aplicación, clasificadas por área de impacto.

## 1. Funcionalidad y Datos 💾
*   **Persistencia de Datos:** Actualmente, si cierras la app, pierdes los prospectos.
    *   *Solución:* Implementar una base de datos ligera (`SQLite`) o guardar automáticamente en un archivo `leads.json` al encontrar un prospecto.
*   **Exportación de Resultados:**
    *   *Mejora:* Agregar un botón "Exportar a Excel/CSV" para que el usuario pueda llevarse la lista y gestionarla en un CRM o Google Sheets.
*   **Historial de Contacto:**
    *   *Mejora:* Marcar visualmente en la lista si ya se hizo clic en el botón de WhatsApp (ej. cambiar el icono de estado a "Contactado ✅").

## 2. Lógica de Scraping (Selenium) 🕷️
*   **Scroll Infinito:** Google Maps carga resultados dinámicamente al hacer scroll.
    *   *Mejora:* Implementar una función que haga scroll en el panel lateral de resultados para cargar más de los 15-20 iniciales antes de empezar a analizar.
*   **Selectores Robustos:** Las clases de Google (como `Nv2y1d` o `qBF1Pd`) cambian frecuentemente.
    *   *Solución:* Usar selectores `XPath` relativos o buscar por atributos más estables (ej. `aria-label`) para reducir el mantenimiento.
*   **Modo "Headless" Opcional:**
    *   *Mejora:* Agregar un Checkbox en la UI para que el usuario decida si quiere ver el navegador abrirse o que corra totalmente oculto.

## 3. Interfaz de Usuario (UI/UX) 🎨
*   **Modernización Visual:**
    *   *Sugerencia:* Migrar de `tkinter` estándar a `CustomTkinter`. Esto permitiría bordes redondeados, modo oscuro nativo y botones más modernos con muy pocos cambios de código.
*   **Feedback de Progreso:**
    *   *Mejora:* Agregar una barra de progreso (`ttk.Progressbar`) indeterminada mientras busca, para que el usuario sepa que la app sigue trabajando.
*   **Control del Proceso:**
    *   *Mejora:* Agregar un botón de "Detener Búsqueda" para cancelar el hilo de ejecución sin tener que cerrar la app a la fuerza.

## 4. Calidad de Código y Arquitectura 🛠️
*   **Separación de Responsabilidades:**
    *   *Refactor:* Mover la lógica de Selenium (`ejecutar_scraping`) a un archivo separado (ej. `scraper_service.py`). Esto hace que el código de la interfaz (`lead_app.py`) quede más limpio.
*   **Manejo de Errores:**
    *   *Mejora:* El `try/except` actual es muy genérico. Sería ideal capturar excepciones específicas (ej. `NoSuchElementException`, `TimeoutException`) para saber si falló el internet, si cambió Google, o si simplemente no hay datos.

## 5. Ideas de Expansión de Negocio 📈
*   **Búsqueda Multi-Ciudad:** Agregar un campo de texto para cambiar "Trelew" por cualquier otra ciudad.
*   **Validación de WhatsApp:** Usar una API (o lógica simple) para verificar si el número extraído es un celular o un fijo (los fijos no suelen tener WhatsApp).

---

### Ejemplo de implementación rápida (Exportar CSV)
```python
import csv
def exportar_csv(self):
    with open('prospectos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Teléfono", "Estado"])
        # ... iterar sobre self.prospectos_datos
```