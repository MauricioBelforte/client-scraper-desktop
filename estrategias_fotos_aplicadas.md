# Registro de Intentos: Extracción de Fotos de Galería (Google Maps)

**Objetivo:** Obtener URLs de imágenes de alta calidad desde la galería "Todas las fotos" de un negocio, en lugar de usar las miniaturas de baja resolución de las reseñas.

**Estado Actual:** 🛑 **Suspendido**. La funcionalidad rompe el flujo del scraper principal, causando que el navegador se cierre o se detenga después del primer negocio.

---

## Estrategias Probadas y Fallos

### 1. Extracción desde Botones de Reseñas (Original)
*   **Método:** Buscar `button[style*='background-image']` dentro de las tarjetas de comentarios.
*   **Resultado:** Funciona y es estable, pero las imágenes son thumbnails de muy baja calidad o recortes.

### 2. Módulo Galería con `ActionChains` y `ESC`
*   **Método:** Abrir galería, hacer scroll con JS, pulsar tecla `ESC` para cerrar.
*   **Fallo:** La galería a menudo no se cerraba. El foco del driver quedaba en el overlay, impidiendo hacer clic en el siguiente negocio de la lista lateral. El script terminaba por error.

### 3. Navegación con `driver.back()`
*   **Método:** Detectar si la URL cambiaba a `/photo/` y usar el botón "Atrás" del navegador.
*   **Fallo:** `driver.back()` es demasiado agresivo. A veces sacaba al robot de la ficha del negocio y lo devolvía a la lista de búsqueda general, rompiendo la referencia de los elementos (`StaleElementReferenceException`) y deteniendo el bucle.

### 4. Detección de Contexto (URL vs Overlay)
*   **Método:** Comparar URL antes y después de abrir la galería para decidir si usar `back()` o cerrar modal.
*   **Fallo:** Inestable. Google Maps maneja el historial de forma compleja (SPA). A veces el robot creía que estaba en un modal y no lo estaba, o viceversa, quedando atrapado.

### 5. Scroll con `scrollIntoView` y Botones UI
*   **Método:** Forzar la carga de imágenes saltando al último elemento (`img`) y buscar botones específicos de la interfaz ("Atrás", "Cerrar") en lugar de usar el teclado.
*   **Fallo:** El scraper procesaba las fotos del primer negocio correctamente, pero al intentar salir, no lograba recuperar el control de la lista de resultados lateral. El navegador se cerraba al no encontrar el siguiente elemento.

### 6. Scroll con Tecla `PAGE_DOWN`
*   **Método:** Simular pulsaciones físicas de teclado para mover el scroll de la galería (que a veces es un `div` difícil de detectar con JS).
*   **Fallo:** Mismo resultado. El problema principal no es el scroll, sino el **retorno seguro** al contexto de la lista de negocios.

---

## Conclusión Técnica

El problema radica en la arquitectura **SPA (Single Page Application)** de Google Maps.

1.  Al entrar en la galería, el DOM cambia drásticamente o se superpone una capa (overlay) que "secuestra" los eventos de ratón y teclado.
2.  Al salir de la galería, aunque visualmente parece que volvemos al mismo lugar, el DOM de la lista de resultados a veces se refresca o pierde el foco, invalidando los elementos web que Selenium tenía guardados en memoria para iterar.

## Pasos a Seguir (Futuro)

Si se retoma esta tarea, se sugiere:
1.  **No entrar a la galería:** Intentar capturar solo las fotos que aparecen en el carrusel horizontal de la ficha principal ("Overview"), sin hacer clic para expandir.
2.  **Nueva Pestaña:** Abrir la galería en una pestaña nueva (`CTRL+CLICK`), extraer las fotos y cerrar la pestaña (`driver.close()`). Esto garantiza que la pestaña original con la lista de negocios permanezca intacta.
3.  **API Oculta:** Investigar si las imágenes se pueden sacar del JSON incrustado en el HTML inicial (`window.APP_INITIALIZATION_STATE`) sin navegar.

*Documento generado automáticamente por Gemini Code Assist.*