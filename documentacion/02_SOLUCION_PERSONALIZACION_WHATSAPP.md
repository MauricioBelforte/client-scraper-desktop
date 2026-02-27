# Solución: Personalización de Mensajes WhatsApp por Categoría

## Problema Identificado

El sistema de personalización de mensajes de WhatsApp no estaba funcionando correctamente porque:

### 1. **Problema de Acentos y Caracteres Especiales**
- Las categorías en los archivos JSON contienen acentos: `Cafetería`, `Peluquería`, `Carnicería`, etc.
- Las palabras clave en el código estaban sin acentos: `cafeteria`, `peluqueria`, `carniceria`
- Al usar `.lower()` se mantenían los acentos, impidiendo que coincidieran

### 2. **Categorías Faltantes en el Diccionario**
El análisis de los archivos JSON reveló estas categorías que no estaban cubiertas:
- `Bufete` (para abogados)
- `Carnicería`
- `Kiosco`
- `Tienda de productos para mascotas` (requería palabra clave "mascota")
- `Tienda de muebles` (requería palabra clave "mueble")
- `Estudio de tatuajes` (requería palabra clave "tatuaje")

### 3. **Falta de Normalización de Caracteres**
No había un método para normalizar el texto (remover acentos) antes de hacer las comparaciones.

## Solución Implementada

### 1. **Nueva Función `normalizar_texto()`**
```python
def normalizar_texto(texto):
    """
    Normaliza el texto removiendo acentos y convirtiendo a minúsculas.
    Esto permite comparar categorías como 'Cafetería' con 'cafeteria'.
    """
    texto_nfd = unicodedata.normalize('NFD', str(texto).lower())
    return ''.join(char for char in texto_nfd if not unicodedata.combining(char))
```

Esta función:
- Convierte a minúsculas
- Elimina acentos usando descomposición Unicode (NFD)
- Permite comparaciones sin importar los acentos

### 2. **Categorías Nuevas Agregadas al Diccionario**

```python
"bufete": { ... }           # Para "Bufete"
"carniceria": { ... }       # Para "Carnicería"
"kiosco": { ... }           # Para "Kiosco"
"mascota": { ... }          # Para "Tienda de productos para mascotas"
"mueble": { ... }           # Para "Tienda de muebles"
"tatuaje": { ... }          # Para "Estudio de tatuajes" (alternativa a "tattoo")
```

### 3. **Mejora de la Función `generar_mensaje_whatsapp()`**

**Antes:**
```python
categoria_lower = str(categoria).lower()
```

**Después:**
```python
categoria_normalizada = normalizar_texto(categoria)
```

Ahora la función normaliza la categoría antes de buscar coincidencias.

## Cobertura de Categorías

Todas las siguientes categorías de los JSON ahora tienen un mensaje personalizado:

| Categoría | Palabra Clave | Estado |
|-----------|---------------|--------|
| Abogado | abogado | ✓ |
| Bufete | bufete | ✓ |
| Inmobiliaria | inmobiliaria | ✓ |
| Arquitecto | arquitecto | ✓ |
| Contable | contable | ✓ |
| Constructora | constructora | ✓ |
| Restaurante | restaurante | ✓ |
| Bar | bar | ✓ |
| Cafetería | cafeteria | ✓ |
| Cervecería | cerveceria | ✓ |
| Pizzería | pizzeria | ✓ |
| Pastelería | pasteleria | ✓ |
| Panadería | panaderia | ✓ |
| Heladería | heladeria | ✓ |
| Catering | catering | ✓ |
| Carnicería | carniceria | ✓ |
| Kiosco | kiosco | ✓ |
| Gimnasio | gimnasio | ✓ |
| Odontólogo | odontologo | ✓ |
| Veterinario | veterinario | ✓ |
| Pet Shop / Mascota | mascota | ✓ |
| Farmacia | farmacia | ✓ |
| Psicólogo | psicologo | ✓ |
| Nutricionista | nutricionista | ✓ |
| Kinesiólogo | kinesiologo | ✓ |
| Peluquería | peluqueria | ✓ |
| Estética | estetica | ✓ |
| Barbería | barberia | ✓ |
| Tatuajes | tatuaje | ✓ |
| Taller Mecánico | taller | ✓ |
| Muebles | mueble | ✓ |
| Otros | (por defecto) | ✓ |

## Cómo Funciona Ahora

1. Se obtiene la categoría del negocio (ej: "Cafetería")
2. Se normaliza: "cafeteria" (sin acentos, minúscula)
3. Se busca si alguna palabra clave está contenida en la categoría normalizada
4. Si hay coincidencia, se usa la plantilla específica
5. Si no, se usa la plantilla por defecto

## Ejemplo

**Entrada:**
- Nombre: "Café del Centro"
- Categoría: "Cafetería"

**Proceso:**
- Normalizar: "cafeteria"
- Buscar "cafeteria" en "cafeteria" ✓ Encontrado
- Usar plantilla de cafeterías

**Resultado:** Mensaje personalizado para cafeterías

## Archivos Modificados

- `src/mensajes.py` - Agregada función `normalizar_texto()` y categorías faltantes

## Archivos Creados para Testing

- `test_mensajes_personalizados.py` - Script para probar todas las categorías

## Recomendaciones

1. Ejecuta `python test_mensajes_personalizados.py` después de actualizar categorías
2. Si necesitas agregar más rubros, simplemente agrega una nueva entrada en `TEMPLATES_POR_RUBRO`
3. La función `normalizar_texto()` maneja automáticamente acentos y mayúsculas
