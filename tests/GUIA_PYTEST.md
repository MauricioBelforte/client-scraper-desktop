# 🧪 Guía Definitiva de Pytest para Python (Versión Actualizada)

Esta guía explica cómo escribir, organizar y ejecutar pruebas automatizadas en este proyecto usando `pytest`. 

## Índice
1. Cómo funciona pytest
2. Estructura de archivos
3. Convención de nombres
4. Cómo escribir funciones de test
5. Ejecución de tests
6. Mocks y fixtures
7. Configuración del proyecto (pytest.ini)

---

## Cómo funciona pytest

### ¿Qué busca pytest automáticamente?

Pytest **escanea recursivamente** directorios en busca de archivos y funciones que cumplan con patrones específicos:

#### 1. **Archivos de test**: pytest busca archivos que coincidan con estos patrones:
   - `test_*.py` → `test_crear_scraper.py` ✅
   - `*_test.py` → `crear_scraper_test.py` ✅
   - `*_test_*.py` → `4_1_13_test_crear_scraper.py` ✅ (patrón usado en este proyecto)

   **Archivos que se ignoran o evitan** en pytest (sin una configuración especial):
   - `src/test_vision.py` → no es un módulo de prueba de verdad, es un experimento
   - `utils.py`, `helpers.py` → no se recopilan porque no coinciden con el patrón

#### 2. **Funciones de test**: dentro de un archivo de test, pytest busca todas las funciones que:
   - Comiencen con `test_` → `test_crear_opciones()` ✅
   - Estén dentro de una clase que comience con `Test` → `class TestScraper: test_method()` ✅

### ¿Por qué no se recopilaban los tests al principio?

El archivo `pytest.ini` define **dónde** buscar. Si la configuración dice `tests` (estándar) pero tu carpeta física se llama `test`, pytest no encontrará nada automáticamente.

```ini
[pytest]
testpaths = tests          # Carpeta estándar (en plural)
python_files = test_*.py *_test.py *_test_*.py
norecursedirs = src
```

**Solución:** Renombramos la carpeta `test` a `tests` para cumplir con el estándar y la configuración.

---

## Estructura de archivos

En este proyecto, usamos la carpeta estándar `tests/`:

```
tests/
├── refactorizacion/           # Tests relacionados con refactorizaciones
│   ├── 1_test_constants.py
│   ├── 2_test_utilidades.py
│   ├── 3_test_constants_cleanup.py
│   └── fase-4-1-configuracion-arranque/
│       ├── 4_1_13_test_crear_clase_scraper.py
│       ├── 4_1_14_test_configuracion_de_opciones.py
│       ├── 4_1_15_test_inicializar_driver.py
│       ├── 4_1_16_test_navegar_a_maps.py
│       └── 4_1_17_test_esperar_feed.py
├── conftest.py                # Configuración compartida entre tests
└── GUIA_PYTEST_2.md           # Este documento
```

**Regla de oro**: Pytest encontrará los tests en cualquier subcarpeta dentro de `tests/` siempre que el archivo cumpla con el patrón de nombres.

---

## Convención de nombres

### Archivos de test

**Formato recomendado** en este proyecto:

```
<número_fase>_<número_ítem>_test_<descripción_español>.py
```

**Ejemplos correctos** (siempre en español):
- `4_1_13_test_crear_clase_scraper.py` ✅
- `4_1_14_test_configuracion_de_opciones.py` ✅
- `2_test_utilidades.py` ✅

### Funciones de test

Siempre deben **comenzar con `test_`** y tener **nombres descriptivos**:

```python
# ✅ Correcto
def test_crear_opciones_chrome(): ...
def test_inicializar_driver_con_mock(): ...
```

---

## Cómo escribir funciones de test

### Estructura básica

```python
import pytest
from src.mi_modulo import MiClase

def test_mi_funcionalidad():
    # ARRANGE: preparar los datos/mocks
    obj = MiClase()
    
    # ACT: ejecutar el código a probar
    resultado = obj.hacer_algo()
    
    # ASSERT: verificar que el resultado es el esperado
    assert resultado == valor_esperado, "Mensaje de error si falla"
```

### Tests Parametrizados (¡Nuevo!)

Para evitar repetir código cuando queremos probar la misma función con diferentes datos (como hicimos con los números de teléfono), usamos el decorador `@pytest.mark.parametrize`.

**Antes (Repetitivo):**
```python
def test_telefono():
    assert limpiar("0280") == "280"
    assert limpiar("1544") == "44"  # Tendríamos que escribir una línea por caso
```

**Ahora (Parametrizado):**
```python
@pytest.mark.parametrize("entrada, esperado", [
    ("0280", "280"),
    ("1544", "44"),
    ("(280)", "280"),
])
def test_telefono_limpio(entrada, esperado):
    # Este test se ejecutará 3 veces automáticamente con los distintos valores
    assert limpiar(entrada) == esperado
```
Esto hace que el reporte de tests sea más detallado y el código más limpio.

### Patrón TDD (Test-Driven Development)

En este proyecto seguimos el patrón **Red-Green-Refactor**:

1. **RED** 🔴: Escribir un test que falla (el método aún no existe)
2. **GREEN** 🟢: Implementar el método mínimo para que pase
3. **REFACTOR** 🔵: Mejorar el código manteniendo el test verde

---

## Ejecución de tests

### Ejecutar todos los tests

Si la carpeta se llama `tests` y `pytest.ini` está configurado correctamente:
   ```powershell
   python -m pytest
   ```

O sino tambien
   ```bash
   python -m pytest tests/ -v
   ```




### Ejecutar una carpeta o archivo específico

1. **Un archivo específico:**
   ```bash
   python -m pytest tests/refactorizacion/4_test_ficha_tecnica.py -v
   ```

2. **Todos los tests de refactorización:**
   ```bash
   python -m pytest tests/refactorizacion/ -v
   ```

3. **Tests de una fase específica:**
   ```bash
   python -m pytest tests/refactorizacion/fase-4-1-configuracion-arranque -v
   ```

4. **Filtrar por nombre de test (`-k`):**
   ```bash
   python -m pytest -k "crear_clase_scraper" -v
   ```

### Opciones útiles

```powershell
# -q: modo quiet (solo resumen)
python -m pytest tests/refactorizacion/ -q

# -v: modo verbose (detalles de cada test)
python -m pytest tests/refactorizacion/ -v

# --tb=short: reporte corto de errores (traceback)
python -m pytest --tb=short

# -x: para en el primer error
python -m pytest -x
```

---

## Configuración del proyecto (pytest.ini)

Este archivo en la raíz controla cómo pytest busca y ejecuta tests:

```ini
[pytest]
# Carpeta donde buscar tests (Estándar: tests)
testpaths = tests

# Patrones de nombres de archivos a considerar como tests
python_files = test_*.py *_test.py *_test_*.py

# Carpetas a no incluir en la búsqueda
norecursedirs = src

# Mostrar prints en tests
addopts = -s
```

---

**Última actualización**: 28 de febrero de 2026