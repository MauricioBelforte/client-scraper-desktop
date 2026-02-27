# REFACTOR: Personalización de Mensajes WhatsApp por Archivo JSON

## Estado: EN PROGRESO

## Descripción General

Refactorización del sistema de personalización de mensajes de WhatsApp para usar el **nombre del archivo JSON** en lugar de la **categoría individual de cada negocio**.

### Problema Original
- Archivo JSON: `Cervecerías.json` ✓ (define claramente el rubro)
- Categoría por negocio: Variable ("Cervecería artesanal", "Fábrica de cerveza", "Bar", etc.) ✗
- Resultado: Complejo matching de palabras clave, 951 negocios sin detectar

### Solución Implementada
- Si carga desde `Cervecerías.json` → Usa automáticamente template de cervecería
- Si carga desde `Restaurantes.json` → Usa automáticamente template de restaurante
- Eliminación completa de búsqueda de palabras clave
- **100% de cobertura garantizada** para archivos configurados

## Fases del Refactor

### Fase 1: Cambios en el Código (ACTUAL)
- [ ] Modificar `lead_app.py` para pasar nombre del archivo
- [ ] Actualizar `generar_mensaje_whatsapp()` en `src/mensajes.py`
- [ ] Simplificar diccionario de templates

### Fase 2: Testing
- [ ] Suite de tests unitarios
- [ ] Tests de integración
- [ ] Tests de extremo a extremo

### Fase 3: Documentación
- [ ] Documentar cambios en detalle
- [ ] Guía de cómo agregar nuevos rubros

### Fase 4: Validación
- [ ] Verificación manual
- [ ] Pruebas en todos los archivos JSON

## Archivos Modificados

| Archivo | Cambio | Estado |
|---------|--------|--------|
| `lead_app.py` | Pasar `self.archivo_activo` a `abrir_whatsapp()` | PENDIENTE |
| `src/mensajes.py` | Refactor `generar_mensaje_whatsapp()` | PENDIENTE |

## Cambios Pendientes

### 1. `lead_app.py` - Función `abrir_whatsapp()`

**Antes:**
```python
def abrir_whatsapp(nombre, telefono, categoria="General"):
    mensaje_codificado = generar_mensaje_whatsapp(nombre, categoria)
```

**Después:**
```python
def abrir_whatsapp(nombre, telefono, nombre_archivo="General"):
    mensaje_codificado = generar_mensaje_whatsapp(nombre, nombre_archivo)
```

### 2. `lead_app.py` - Llamada a `abrir_whatsapp()`

**Antes:**
```python
command=lambda: abrir_whatsapp(nombre, tel, datos.get('categoria', 'General'))
```

**Después:**
```python
command=lambda: abrir_whatsapp(nombre, tel, self.archivo_activo)
```

### 3. `src/mensajes.py` - Función `generar_mensaje_whatsapp()`

**Antes:**
```python
def generar_mensaje_whatsapp(nombre_negocio, categoria):
    categoria_normalizada = normalizar_texto(categoria)
    # Búsqueda compleja de palabras clave...
```

**Después:**
```python
def generar_mensaje_whatsapp(nombre_negocio, nombre_archivo):
    # Mapeo directo nombre_archivo -> template
    config = TEMPLATES_POR_ARCHIVO.get(nombre_archivo, TEMPLATE_DEFAULT)
```

## Ventajas del Refactor

✅ Eliminación de 51 líneas de código complejo
✅ 100% de cobertura para archivos predefinidos
✅ Escalable: agregar rubro = agregar archivo JSON + entry en diccionario
✅ Sin dependencias de categorías internas
✅ Mantenimiento simplificado
✅ Mejor rendimiento (búsqueda O(1) en lugar de O(n))

## Cambios en `src/mensajes.py`

**Estructura anterior:** `TEMPLATES_POR_RUBRO` (búsqueda por palabras clave)
**Estructura nueva:** `TEMPLATES_POR_ARCHIVO` (mapeo directo)

```python
TEMPLATES_POR_ARCHIVO = {
    "Abogados": { "intro": "...", "modelos": [...] },
    "Restaurantes": { "intro": "...", "modelos": [...] },
    "Cervecerías": { "intro": "...", "modelos": [...] },
    ...
}
```

## Impacto en los Usuarios

**Ninguno** - El mensaje recibido es exactamente el mismo, solo el mecanismo para seleccionar el template está optimizado.

## Próximos Pasos

1. Implementar cambios en código
2. Ejecutar suite de tests
3. Validar manualmente
4. Documentar cambios completamente
