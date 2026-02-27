# Estrategia de refactorización por fases y pruebas

Este documento detalla el flujo de trabajo que seguiremos para la ejecución de tests automatizados, que consiste en la reestructuración del código hacia una arquitectura más modular. El objetivo es garantizar que cada cambio esté respaldado por pruebas automatizadas que confirmen que el comportamiento esperado se mantiene intacto.
Los nombres de los tests seguirán un formato específico para facilitar su identificación y organización, y se ubicarán en el subdirectorio Ej:`test/refactorizacion/fase-4-1-configuracion-arranque/`.
Ademas los nombres de los tests deben estar escritos en español y describir claramente lo que se está probando, siguiendo la convención de nombres establecida en el proyecto.

> **Importante**: la carpeta `src` contiene módulos de producción que también tienen nombres como `test_*.py`. Para evitar que pytest intente recopilarlos y falle (como ocurrió al ejecutar `test_vision.py`), se creó un archivo `pytest.ini` en la raíz del proyecto que limita
> la búsqueda a `test/` y excluye `src` (ver sección "Ejecutar los tests" más abajo).



1. **Crear test antes de refactorizar**
   - Para cada ítem del archivo REFACTOR_PLAN_DETALLADO.md se toma por ejemplo los items numerados (del 13 al 17) se generará un archivo de prueba dentro de este subdirectorio. El nombre seguirá el formato
     `4_1_<número>_test_<descr_español>.py`.
   - La prueba deberá comprobar la existencia y/o comportamiento esperado de
     la funcionalidad actual (antes de moverla), de modo que sirva como
     regresión.

2. **Ejecutar el test inicial**
   - Corremos `pytest` en el subdirectorio para asegurarnos de que falla por
     la ausencia de la clase o método.

3. **Implementar la refactorización**
   - Modificar el código en `src/scraper.py` y/o `lead_app.py` para cumplir el
     requisito (crear clase, extraer método, etc.).

4. **Volver a ejecutar el test**
   - El mismo test debe pasar, demostrando que la refactorización no rompió
     el comportamiento esperado.
   - Si el test falla, revisar y ajustar.

5. **Marcar el ítem en el plan**
   - En `REFACTOR_PLAN_DETALLADO.md` se colocará "[x]" junto al ítem.

Este proceso se repetirá para cada sub-ítem hasta completar la fase. La
idea es tener siempre pruebas automatizadas que garanticen que el código
sigue funcionando mientras lo movemos hacia la nueva estructura modular.

> Nota: Los tests en esta carpeta emplearán mocks del driver de Selenium para
> no abrir un navegador real durante la ejecución.

---

### Ejecutar los tests correctamente

1. **Instala las dependencias de pruebas** (hazlo una vez o siempre que
   configures el entorno):

```powershell
cd "<ruta-del-proyecto>"
python -m pip install -r requirements.txt
```

Asegúrate de que los paquetes `pytest` y `pytest-mock` aparezcan en la
salida de `pip list`.

2. **Nunca ejecutes un archivo de prueba aislado con `python`**; en su
   lugar usa el comando global de pytest desde la raíz del proyecto:

```powershell
python -m pytest test/refactorizacion/fase-4-1-configuracion-arranque -q
```

   o bien filtra por palabra clave:

```powershell
python -m pytest -k "wait_for_feed" -q
```

   Gracias al `pytest.ini`, pytest buscará únicamente dentro de `test/` y
   no se equivocará recogiendo archivos como los de `src/`.
```

Como ejecutarlos?

Ejemplo para ejecutarlos a todos dentro de esa carpeta:
python -m pytest test/refactorizacion/fase-4-1-configuracion-arranque -q

Ejemplo para ejecutarlos de a uno:
python -m pytest -k "wait_for_feed" -q