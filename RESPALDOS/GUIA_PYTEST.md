# 🧪 Guía Definitiva de Pytest para Python

Esta guía explica cómo escribir, organizar y ejecutar pruebas automatizadas en este proyecto usando `pytest`. 

## Índice
1. [Cómo funciona pytest](#cómo-funciona-pytest)
2. [Estructura de archivos](#estructura-de-archivos)
3. [Convención de nombres](#convención-de-nombres)
4. [Cómo escribe sus funciones de test](#cómo-escribir-funciones-de-test)
5. [Ejecución de tests](#ejecución-de-tests)
6. [Mocks y fixtures](#mocks-y-fixtures)
7. [Configuración del proyecto (pytest.ini)](#configuración-del-proyecto)

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

**Ejemplo: qué hace pytest al ejecutar**:

```
Buscar:     refactorizacion/fase-4-1-configuracion-arranque/
En:	       4_1_13_test_crear_clase_scraper.py (sí, coincide con *_test_*.py)
Adentro:    def test_clase_scraper_existe(): ✅ (comienza con test_)
```

### ¿Por qué no se recopilaban los tests al principio?

El archivo `pytest.ini` **restringía** la búsqueda a qué archivos recopilar:

```ini
[pytest]
testpaths = test           # Solo busca en la carpeta 'test/'
python_files = *_test.py test_*.py   # ❌ No incluía *_test_*.py
norecursedirs = src        # Excluye 'src/' completamente
```

Por eso tu archivo `4_1_13_test_crear_clase_scraper.py` **no se recopilaba**. Lo arreglamos añadiendo:

```ini
python_files = test_*.py *_test.py *_test_*.py   # ✅ Ahora sí recopila
```

---

## Estructura de archivos

En este proyecto, los tests están organizados en categorías:

```
test/
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
└── GUIA_PYTEST.md             # Este documento
```

**Regla de oro**: Pytest encontrará los tests en cualquier subcarpeta dentro de `tests/` siempre que el archivo cumpla con el patrón de nombres.


## Convención de nombres

### Archivos de test

**Formato recomendado** en este proyecto:

```
<número_fase>_<número_ítem>_test_<descripción_español>.py
```

**Ejemplos correctos** (siempre en español):
- `4_1_13_test_crear_clase_scraper.py` ✅
- `4_1_14_test_configuracion_de_opciones.py` ✅
- `4_1_15_test_inicializar_driver.py` ✅
- `test_validar_datos_cliente.py` ✅
- `2_test_utilidades.py` ✅

**Ejemplos incorrectos** (no usar):
- `4_1_14_test_configuration_options.py` ❌ (inglés)
- `test.py` ❌ (demasiado genérico)
- `tests_scraper.py` ❌ (patrón `tests_*`, no estándar)

### Funciones de test

Siempre deben **comenzar con `test_`** y tener **nombres descriptivos**:

```python
# ✅ Correcto
def test_crear_opciones_chrome():
    ...

def test_inicializar_driver_con_mock():
    ...

def test_navegar_a_maps_construye_url_correcta():
    ...

# ❌ Incorrecto
def comprobar_opciones():
    ...

def test_1():
    ...

def test():
    ...
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
    # Este test se ejecutará 3 veces automáticamente
    assert limpiar(entrada) == esperado
```
Esto hace que el reporte de tests sea más detallado y el código más limpio.

### Patrón TDD (Test-Driven Development)

En este proyecto seguimos el patrón **Red-Green-Refactor**:

1. **RED** 🔴: Escribir un test que falla (el método aún no existe)
2. **GREEN** 🟢: Implementar el método mínimo para que pase
3. **REFACTOR** 🔵: Mejorar el código manteniendo el test verde

Ejemplo:

```python
# test/refactorizacion/fase-4-1-configuracion-arranque/4_1_13_test_crear_clase_scraper.py
def test_clase_scraper_existe():
    """Test RED: Comprueba que la clase Scraper existe (aún no existe)."""
    from src import scraper
    assert hasattr(scraper, 'Scraper'), "La clase Scraper debe estar en src/scraper.py"
```

Una vez escrito este test (que falla), implementamos la clase en `src/scraper.py` para que pase.

---

## Ejecución de tests

### Instalación de dependencias

```powershell
cd "<ruta-del-proyecto>"
python -m pip install -r requirements.txt
```

Verifica que incluyamos:
```
pytest
pytest-mock
```

### Ejecutar todos los tests

Si la carpeta se llama `tests` y `pytest.ini` está configurado correctamente:
```powershell
python -m pytest
```

### Ejecutar una caneta específica


1. Para ejecutar SOLO un test específico:
Este verificará específicamente que el scroll use bind_all y que los textos estén corregidos.

```bash
python -m pytest test/refactorizacion/4_test_ficha_tecnica.py -v
```


2. Para ejecutar TODOS los tests de refactorización
Esto correrá todos los tests que has hecho hasta ahora (constants, utilidades, cleanup y ficha_tecnica).

```bash
python -m pytest test/refactorizacion/ -v
```


3. Para ejecutar todos los tests de la fase 4.1
```bash
python -m pytest test/refactorizacion/fase-4-1-configuracion-arranque -v
```

4. Otro ejemplo para  test específico por nombre
```bash
python -m pytest -k "crear_clase_scraper" -v
```

# Un archivo específico
```
python -m pytest test/refactorizacion/fase-4-1-configuracion-arranque/4_1_13_test_crear_clase_scraper.py -v
```

### Opciones útiles

```powershell
# -q: modo quiet (solo resumen)
python -m pytest test/refactorizacion/fase-4-1-configuracion-arranque -q
# Salida: ..... (5 passed)

# -v: modo verbose (detalles de cada test)
python -m pytest test/refactorizacion/fase-4-1-configuracion-arranque -v
# Salida: 
# test_crear_clase_scraper PASSED
# test_configuracion_de_opciones PASSED
# ...

# --tb=short: reporte corto de errores
python -m pytest --tb=short

# -x: para en el primer error
python -m pytest -x

# --maxfail=2: para después de 2 errores
python -m pytest --maxfail=2
```

---

## Mocks y fixtures

### ¿Por qué usar mocks?

En tests, queremos aislar el código a probar sin efectos secundarios:
- No descargar drivers reales (selenium)
- No hacer llamadas HTTP reales
- No escribir archivos reales

**Mock** = objeto falso que pretende ser algo real.

### Usando monkeypatch (pytest-mock)

```python
def test_método_llamado(monkeypatch):
    """Ejemplo: mockeando webdriver.Chrome"""
    
    # Definir un driver falso
    class FakeDriver:
        pass
    
    # Reemplazar webdriver.Chrome en el módulo scraper
    monkeypatch.setattr('src.scraper.webdriver.Chrome', FakeDriver)
    
    # Ahora cuando tu código importa/usa webdriver.Chrome, usará FakeDriver
    driver = webdriver.Chrome(...)  # Usa FakeDriver, no el real
```

### Fixtures (funciones reutilizables)

```python
# test/conftest.py
import pytest

@pytest.fixture
def dummy_driver():
    """Fixture que proporciona un driver falso a todos los tests."""
    class DummyDriver:
        def __init__(self):
            self.current_url = None
    return DummyDriver()

# test/refactorizacion/.../algún_test.py
def test_navegar(dummy_driver):
    """El fixture dummy_driver se inyecta automáticamente."""
    assert dummy_driver is not None
```

### Conftest.py

Este archivo especial en `test/conftest.py` contiene:
- Fixtures compartidas entre todos los tests
- Configuración de path (para imports)
- Hooks de pytest

En nuestro proyecto, `test/conftest.py` asegura que `sys.path` incluya la raíz, permitiendo `from src.modulo import ...`.

---

## Configuración del proyecto

### pytest.ini

Este archivo en la raíz controla cómo pytest busca y ejecuta tests:

```ini
[pytest]
# Carpeta donde buscar tests
testpaths = test

# Patrones de nombres de archivos a considerar como tests
python_files = test_*.py *_test.py *_test_*.py

# Carpetas a no incluir en la búsqueda
norecursedirs = src

# Mostrar prints en tests
addopts = -s
```

**Por qué tenemos `norecursedirs = src`**: evita que pytest intente recopilar archivos como `src/computer_vision_desatendida/test_vision.py`, que no son truly test files sino experimentos.

---

## Checklist para nuevo test

Cuando crees un nuevo test, sigue este checklist:

- [ ] Archivo en carpeta `tests/` con nombre `*_test_*.py` (en español)
- [ ] Función comienza con `test_`
- [ ] Descripción clara en el nombre (qué se prueba)
- [ ] Docstring explicando la intención
- [ ] Estructura ARRANGE → ACT → ASSERT
- [ ] Usar mocks si es necesario (monkeypatch, fixtures)
- [ ] Ejecutar localmente: `python -m pytest [archivo]`
- [ ] Que pase el test
- [ ] Documentar en el plan si es parte de una refactorización

---

## Recursos adicionales

- [Documentación oficial de pytest](https://docs.pytest.org/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Testing Best Practices](https://docs.pytest.org/en/7.1.x/goodpractices.html)

---

**Última actualización**: 27 de febrero de 2026  
**Responsable**: Proyecto Recolecta Emprendimientos




---
COLOCALO ANTES DE ESTO