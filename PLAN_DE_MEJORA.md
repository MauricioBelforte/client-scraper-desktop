# 📋 Plan de Refactorización: Estrategias Desacopladas y Gestor de Fusión

## 1. Contexto y Problema
Actualmente, el robot intenta aplicar dos estrategias de scroll (JavaScript y Teclado) secuencialmente sobre el mismo elemento.
**El conflicto:** La velocidad del JS combinada con la simulación de foco del teclado provoca que, ocasionalmente, se haga clic sobre una imagen de la galería en lugar del panel vacío, abriendo el visor de fotos y rompiendo el flujo de navegación.

## 2. Solución Propuesta
Separar el proceso de recolección en dos vías independientes y crear una instancia posterior de curación de datos (Fusión).

### A. Extracción (Scraping)
- **Desacople:** En lugar de un botón único de "Buscar", tendremos dos opciones claras en la interfaz.
- **Salida:** Cada estrategia generará su propio archivo de "crudos" (raw data) para no sobrescribir ni mezclar datos automáticamente con riesgo de error.
  - `cerveceria_rapido.json` (Estrategia JS)
  - `cerveceria_humano.json` (Estrategia Teclado)

### B. Transformación y Carga (Gestor de Fusión)
- **Nueva Interfaz:** Una ventana o pestaña dedicada a la gestión de estos archivos JSON.
- **Funcionalidad:**
  - Cargar dos archivos del mismo rubro (ej. la versión rápida y la humana).
  - Comparar campos (Teléfono, Web, Redes).
  - Permitir al usuario elegir qué dato es el correcto o editarlo manualmente.
  - Generar un archivo "Maestro" (`cerveceria_final.json`) limpio y verificado.

---

## 3. Checklist de Implementación

### Fase 1: Interfaz de Búsqueda (UI Principal)
- [x] Modificar `setup_ui` en `lead_app.py`.
- [x] Reemplazar el botón actual "BUSCAR Y GUARDAR" por dos botones:
  - [x] ⚡ **Modo Rápido (JS)**: Ejecuta `estrategia_scroll_js_focalizado`.
  - [x] 👤 **Modo Humano (Teclado)**: Ejecuta `estrategia_scroll_teclado`.
- [x] Agregar tooltips o etiquetas que expliquen la diferencia (Velocidad vs. Profundidad).

### Fase 2: Lógica de Scraping y Guardado
- [ ] Refactorizar `ejecutar_scraping` para aceptar un argumento `modo_estrategia`.
- [ ] Modificar la lógica de guardado de archivos:
  - Si es Modo Rápido -> Guardar como `{rubro}_v1_js.json`.
  - Si es Modo Humano -> Guardar como `{rubro}_v2_key.json`.
- [ ] Asegurar que la lectura de archivos previos (histórico) no mezcle versiones automáticamente al iniciar.

### Fase 3: Nuevo Módulo "Gestor de Datos" (Data Merger)
- [ ] Crear nueva clase/ventana `VentanaFusionDatos`.
- [ ] **Diseño UI:**
  - [ ] Selector de Archivo A (Izquierda).
  - [ ] Selector de Archivo B (Derecha).
  - [ ] Lista central de conflictos o coincidencias.
- [ ] **Lógica de Comparación:**
  - [ ] Algoritmo que detecte si un negocio está en ambos archivos.
  - [ ] Resaltar diferencias (ej. A tiene email, B no).
- [ ] **Edición Manual:**
  - [ ] Permitir editar campos de texto antes de guardar.
- [ ] **Guardado Final:**
  - [ ] Botón "Generar Ficha Maestra" -> Guarda `{rubro}_MASTER.json`.

### Fase 4: Limpieza
- [ ] Eliminar código antiguo de estrategias combinadas.
- [ ] Actualizar `constants.py` con los nuevos sufijos de archivo.