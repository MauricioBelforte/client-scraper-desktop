# Guía: Agregar Nuevos Rubros

Esta guía explica cómo agregar soporte para un nuevo rubro (ej: "Ferreterías") al sistema de mensajería.

---

## Pasos para Agregar un Nuevo Rubro

### Paso 1: Crear archivo JSON

Crear archivo en `fichas_leads/NombreDelRubro.json` con tu estructura de datos.

**Ejemplo**:
```json
{
  "fichas": [
    {
      "nombre": "Ferretería Central",
      "telefono": "+5492965123456",
      "direccion": "Calle Principal 100",
      "categoria": "Ferretería de materiales"
    },
    {
      "nombre": "Todo Construcción",
      "telefono": "+5492965789012",
      "direccion": "Avenida Mitre 200",
      "categoria": "Ferretería mayorista"
    }
  ]
}
```

**Importante**: El nombre del archivo (sin extensión) será la clave para acceder a la plantilla.
- `Ferreterías.json` → clave `"Ferreterías"`
- `Peluquerías.json` → clave `"Peluquerías"`

---

### Paso 2: Agregar Entrada en `TEMPLATES_POR_ARCHIVO`

Editar `src/mensajes.py` e insertar nueva entrada en diccionario `TEMPLATES_POR_ARCHIVO`:

```python
TEMPLATES_POR_ARCHIVO = {
    # ... Rubros existentes ...
    
    "Ferreterías": {
        "intro": "Estoy ofreciendo mis servicios a ferreterías y comercios de materiales de construcción.",
        "modelos": [
            "Modelo 1: https://ejemplo1.netlify.app/",
            "Modelo 2: https://ejemplo2.netlify.app/",
            "Modelo 3: https://ejemplo3.netlify.app/"
        ]
    },
    
    # ... Más rubros ...
}
```

### Estructura requerida:
- **Clave**: Debe coincidir exactamente con nombre del archivo JSON (sin .json)
- **intro**: Texto inicial del mensaje personalizado para este rubro
- **modelos**: Lista de URLs de plantilla disponibles

---

### Paso 3: Verificar Integración

Una vez agregado, el sistema automáticamente:
1. Reconocerá el archivo JSON cuando se cargue en la UI
2. Usará la plantilla asociada para generar mensajes
3. No requiere cambios en `lead_app.py` ni otras partes del código

---

## Ejemplo Completo: Agregar "Ferreterías"

### Archivo: `fichas_leads/Ferreterías.json`
```json
{
  "fichas": [
    {
      "nombre": "Ferretería Central",
      "telefono": "+5492965123456",
      "categoria": "Ferretería de materiales"
    }
  ]
}
```

### Cambio en `src/mensajes.py`:
```python
"Ferreterías": {
    "intro": "Estoy ofreciendo mis servicios a ferreterías y comercios de construcción.",
    "modelos": [
        "Modelo 1: https://construccion-patagonica.netlify.app/",
        "Modelo 2: https://materiales-trelew.netlify.app/"
    ]
},
```

### Flujo en la aplicación:
1. Usuario carga `Ferreterías.json` → `self.archivo_activo = "Ferreterías"`
2. Usuario selecciona "Ferretería Central" y hace click en WhatsApp
3. `abrir_whatsapp("Ferretería Central", "+5492965123456", "Ferreterías")`
4. `generar_mensaje_whatsapp("Ferretería Central", "Ferreterías")`
5. Busca: `TEMPLATES_POR_ARCHIVO["Ferreterías"]`
6. Obtiene intro personalizado + 2 modelos
7. Genera mensaje URL-encoded y abre WhatsApp

---

## Casos Especiales

### Nombre de archivo con espacios

Si el archivo se llama `Pet Shops.json`:
- En el sistema operativo: `Pet Shops.json`
- En diccionario: `"Pet Shops"` (con espacios)

```python
"Pet Shops": {
    "intro": "Estoy ofreciendo mis servicios a veterinarias y pet shops.",
    "modelos": ["..."]
},
```

### Fallback a Template Default

Si cargas un archivo `MiRubroCustomizado.json` sin entrada en `TEMPLATES_POR_ARCHIVO`:
```python
# Automáticamente usa:
TEMPLATE_DEFAULT = {
    "intro": "Estoy ofreciendo mis servicios a distintos negocios y profesionales locales.",
    "modelos": [5 modelos genéricos]
}
```

No genera error, sino que proporciona mensaje genérico.

---

## Estructura Recomendada para `intro`

Seguir este patrón para consistencia:

```python
"Introducción genérica a tu categoría + contexto local/específico"

Ejemplos:
- "Estoy ofreciendo mis servicios a ferreterías y comercios de construcción."
- "Estoy ofreciendo mis servicios a psicólogos y profesionales de la salud mental."
- "Estoy ofreciendo mis servicios a gymnasios y centros de fitness locales."
```

---

## Seleccionar URLs de Plantillas

Para cada rubro, necesitas URLs de plantillas que hayas creado. Ejemplo:

```python
"modelos": [
    "Modelo 1: https://ferreteria-central-demo.netlify.app/",
    "Modelo 2: https://construccion-patagonica.netlify.app/",
    "Modelo 3: https://materiales-trelew.netlify.app/"
]
```

**Notas**:
- Debe ser URL completa (http o https)
- Las URLs se envían literalmente en el mensaje de WhatsApp
- Usuario puede hacer click directo desde WhatsApp

---

## Validación Post-Agregación

Después de agregar nuevo rubro, puedes validar con:

```bash
# Ejecutar tests
python -m pytest test/1_test_nuevo_sistema_mensajes.py -v

# Verificar que TEMPLATES_POR_ARCHIVO contiene la entrada
python -c "from src.mensajes import TEMPLATES_POR_ARCHIVO; print('Ferreterías' in TEMPLATES_POR_ARCHIVO)"
# Debe imprimir: True
```

---

## Resumen

| Tarea | Ubicación |
|-------|-----------|
| Crear JSON | `fichas_leads/NuevoRubro.json` |
| Agregar template | `src/mensajes.py` - `TEMPLATES_POR_ARCHIVO` |
| Poblar datos | Usuario carga JSON en la UI |
| Testing | `test/1_test_nuevo_sistema_mensajes.py` |

**Resultado**: El nuevo rubro funciona automáticamente en toda la aplicación sin cambios adicionales.
