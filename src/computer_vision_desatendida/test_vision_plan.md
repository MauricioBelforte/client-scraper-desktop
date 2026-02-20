# 🤖 Plan de Ejecución para Agente Autónomo: Reparación de Visión por Computadora

**Rol:** Agente de DevOps / Backend Python.
**Objetivo:** Restablecer la funcionalidad de clasificación de imágenes (Zero-Shot) usando la API de Hugging Face, superando los errores de enrutamiento (404/410).

## ⚠️ Restricciones (Strict Mode)
Solo tienes permiso para leer/escribir en:
1.  `fichas_leads/test_vision.py` (Script de prueba)
2.  `fichas_leads/test_vision_plan.md` (Este archivo de bitácora)
3.  `src/estrategia_fotos_reviews.py` (Solo funciones `analizar_contenido_clip` y `analizar_imagen_ia`)

**Permisos:**
- Ejecutar comandos en consola (para correr el test).
- Leer logs de salida.

---

## 🚨 Diagnóstico del Último Fallo
**Error Reportado:**
- `https://router.huggingface.co/hf-inference/models/...` -> **404 Not Found** (Ruta incorrecta).
- `https://api-inference.huggingface.co/models/...` -> **410 Gone** (Dominio deprecado).

**Conclusión:**
La estructura de URL para el nuevo `router` de Hugging Face no lleva el prefijo `/hf-inference/` para este modelo, o requiere una estructura diferente. La librería oficial falló con `StopIteration`, lo que sugiere que la respuesta cruda no es lo que espera, o la conexión se corta.

---

## 🧪 Plan de Acción Inmediato (Iteración Actual)

### Paso 1: Corrección de URLs en `src/estrategia_fotos_reviews.py`
Vamos a probar la ruta directa al modelo en el router, sin prefijos extraños, y una alternativa de pipeline.

**URLs a inyectar en `posibles_urls`:**
1.  `https://router.huggingface.co/models/openai/clip-vit-base-patch32` (Estándar nueva)
2.  `https://router.huggingface.co/pipeline/zero-shot-image-classification/openai/clip-vit-base-patch32` (Explícita)

### Paso 2: Ejecución del Test
Ejecutar: `python fichas_leads/test_vision.py`

### Paso 3: Análisis de Respuesta
- Si **200 OK**: ¡Éxito! Documentar URL ganadora.
- Si **503 Service Unavailable**: El modelo está cargando. El script ya tiene lógica de espera. Dejar correr.
- Si **404/400**: El modelo `openai/clip-vit-base-patch32` podría estar restringido o movido.
    - **Plan B (Contingencia):** Cambiar el modelo a uno más moderno/disponible como `laion/CLIP-ViT-B-32-laion2B-s34B-b79K` o volver a clasificación simple con `google/vit-base-patch16-224`.

---

## 📝 Bitácora de Cambios (Agent Log)

- **[INTENTO 1]** Uso de librería `huggingface_hub`. **Fallo:** `StopIteration`.
- **[INTENTO 2]** Uso de `requests` con `router/hf-inference`. **Fallo:** 404.
- **[INTENTO 3 - ACTUAL]** Uso de `requests` con `router/models` directo.
