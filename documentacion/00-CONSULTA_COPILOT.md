# Consulta: Scroll Infinito en Google Maps (Selenium) fallando en layouts dinámicos

## Stack
- Python 3.x
- Selenium WebDriver (Chrome)
- Windows

## Objetivo
Hacer scroll infinito en el panel lateral de reseñas de Google Maps para cargar todos los comentarios de un negocio.

## Problema Actual
El script falla en detectar o mover el scroll en ciertos tipos de negocios, específicamente aquellos que tienen secciones extra como el botón **"Pedir en línea"** o **"Reservar"** en la parte superior del panel lateral.
- **Negocios Normales:** El scroll solía funcionar.
- **Negocios con "Pedir en línea":** El contenido de reseñas está desplazado hacia abajo y anidado diferente. El script no logra bajar.

## Métodos Probados (y por qué fallaron)

### 1. ActionChains con Coordenadas (Click + PageDown)
Calculamos coordenadas (ej. `window.innerWidth * 0.25`, `window.innerHeight * 0.60`) para hacer clic y dar foco.
**Fallo:** En layouts con "Pedir en línea", las coordenadas calculadas caen sobre elementos flotantes (como el botón de ayuda `?` o el footer) o fuera del contenedor de scroll, impidiendo que `PAGE_DOWN` funcione.

### 2. JavaScript: `scrollIntoView`
```javascript
arguments[0].scrollIntoView({block: "center"});
```
**Fallo:** Visualmente mueve el elemento, pero a menudo no dispara el evento de "carga" (XHR) de Google Maps para traer más reseñas.

### 3. JavaScript: Manipulación de `scrollTop`
Intentamos buscar el contenedor padre con scroll:
```javascript
var parent = element.parentElement;
while (parent) {
    if (parent.scrollHeight > parent.clientHeight) {
        parent.scrollTop = parent.scrollHeight;
    }
    parent = parent.parentElement;
}
```
**Fallo:** En estructuras complejas (con "Pedir en línea"), a veces selecciona un contenedor padre incorrecto (ej. el `body` o un wrapper externo) que no controla el scroll de la lista de reseñas, o simplemente no tiene efecto.

### 4. JavaScript: `WheelEvent`
```javascript
element.dispatchEvent(new WheelEvent('wheel', { deltaY: 1000, bubbles: true }));
```
**Fallo:** No logramos que el evento burbujee correctamente al contenedor que tiene el `overflow: scroll` en todos los casos.

## Pregunta
¿Existe una forma más robusta (quizás usando selectores específicos de Google Maps como `div[role='main']` o similar, o una simulación de eventos diferente) para garantizar que el scroll baje siempre, independientemente de si hay botones extra en la cabecera del panel?