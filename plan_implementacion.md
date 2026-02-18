# 📋 Plan de Automatización: Generador Web con IA

Este documento sirve como hoja de ruta para automatizar la creación de sitios web para emprendimientos, integrando Google Gemini para la generación de contenido y limpieza de datos.

## Phase 1: Configuración y Entorno 🛠️
- [x] 1. **Instalar dependencias**: Asegurar que `google-generativeai` esté instalado en el entorno virtual.
- [x] 2. **Gestión de Secretos**: Crear un archivo `.env` o variable de entorno para proteger la `API_KEY` de Gemini.
- [x] 3. **Estructura de Directorios**: Verificar que la carpeta `sitios/` exista y tenga permisos de escritura.
- [x] 4. **Análisis de Reglas**: Leer y analizar el archivo `sitios/instrucciones_sistema.md` para extraer las reglas de estilo, tono y estructura obligatorias.

## Phase 2: Módulo de Inteligencia Artificial (Gemini) 🧠
- [x] 5. **Crear `controlador_ia.py`**: Crear un nuevo script dedicado exclusivamente a la comunicación con la API.
- [x] 6. **Ingeniería de Prompts (Contenido)**: Refinar el prompt para que Gemini genere no solo el "Hero" y "Descripción", sino también beneficios clave basados en las reseñas.
- [x] 7. **Ingeniería de Prompts (Limpieza)**: (Opcional) Crear una función que use Gemini para estandarizar el JSON sucio del scraper (ej: corregir formatos de teléfono, capitalizar nombres).
- [x] 8. **Manejo de Errores**: Implementar lógica de reintento (retry) si la API de Gemini falla o devuelve un JSON malformado.
- [x] 9. **Validación de JSON**: Asegurar que la respuesta de la IA sea un JSON válido antes de pasarlo al generador.

## Phase 3: Mejora del Generador Web (`generador_web.py`) 🎨
- [x] 10. **Adaptación a IA**: Modificar `generar_web_profesional` para que priorice los textos de la IA sobre los genéricos, pero mantenga fallbacks robustos.
- [x] 11. **Inyección de CSS Mejorado**: Actualizar la variable `CSS_MASTER` incorporando las pautas de diseño de `instrucciones_sistema.md` (tipografías, paleta de colores, espaciados).
- [x] 12. **Estructura de Carpetas por Cliente**: Confirmar que el script crea `sitios/{slug_negocio}/index.html` y copia/descarga los assets necesarios (imágenes).
- [x] 13. **Metadatos y SEO**: Agregar meta tags dinámicos (description, keywords) basados en la info del negocio.

## Phase 4: Integración del Flujo (El "Botón") 🔗
- [x] 14. **Script Orquestador (`main.py`)**: Crear un script principal que simule el "botón". Recibe un JSON de entrada y ejecuta la cadena: `IA -> Generador`.
- [x] 15. **Interfaz de Selección (CLI/GUI)**: Opción A: Un menú simple en consola para elegir un negocio de la lista del scraper.
- [x] 16. **Interfaz de Selección (CLI/GUI)**: Opción B: Una función que se pueda llamar desde tu interfaz actual de "Ficha de emprendimiento".
- [x] 17. **Feedback Visual**: Agregar prints o logs que indiquen: "⏳ Generando textos...", "✅ Web creada en...", "❌ Error en...".

## Phase 5: Testing y Calidad ✅
- [x] 18. **Prueba Unitaria (IA)**: Ejecutar solo el módulo de IA con un JSON de prueba para ver la calidad de los textos.
- [x] 19. **Prueba de Integración**: Correr el flujo completo para un negocio real (ej: una veterinaria).
- [x] 20. **Revisión Visual**: Abrir el `index.html` generado y verificar responsividad (móvil/escritorio) y que las imágenes generadas carguen bien.
- [x] 21. **Checklist Final**: (Aprobado para Demo) Se considera el resultado actual suficiente para el objetivo de venta. Las mejoras estrictas de SEO/Estilo quedan para una futura iteración.

---

## 📝 Notas de Progreso

*Espacio para anotar observaciones durante el desarrollo.*

- Se decidió posponer la optimización estricta de SEO y fuentes para una fase de "Refinamiento" futura.
- El objetivo actual es tener demos funcionales y atractivas rápidamente, lo cual se ha logrado con éxito.