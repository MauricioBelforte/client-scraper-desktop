"""
Test para validar que la ventana de Ficha Técnica se abre correctamente y muestra datos.

Este test fue creado como regresión después de identificar que la ventana de ficha
técnica aparecía vacía debido a referencias a constantes que no existían en src/constants.py.

**Bug Identificado**: 
- Las constantes ENCABEZADO_FICHA, SECCION_COMENTARIOS, MSJ_SIN_COMENTARIOS y NOTA_PIE
  fueron removidas de src/constants.py durante la refactorización, pero seguían siendo
  usadas en lead_app.py en la función mostrar_info_detallada().
  
**Síntoma**: La ventana abría pero mostraba contenido vacío en los labels.

**Solución**: Reemplazar todas las referencias a constantes faltantes con literales en español.

**Archivos Afectados**: lead_app.py (líneas 438, 836, 890, 900, 903)
"""

import pytest


def test_botón_ficha_tecnica_texto_actualizado():
    """
    Verifica que el botón 'VER FICHA TÉCNICA' haya sido actualizado
    (anteriormente decía 'VER FICHA TÉCNICA (WEB DEMO)').
    """
    with open("lead_app.py", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    # Verificar que el texto del botón NO contiene "(WEB DEMO)"
    assert "VER FICHA TÉCNICA (WEB DEMO)" not in contenido, \
        "El botón aún contiene el texto '(WEB DEMO)' que debería haber sido removido"
    
    # Verificar que el texto correcto existe
    assert "VER FICHA TÉCNICA" in contenido, \
        "El botón debe contener 'VER FICHA TÉCNICA'"


def test_no_referencias_a_constantes_faltantes():
    """
    Verifica que no existan referencias a constantes que fueron removidas.
    
    Constantes que no deberían existir más en lead_app.py:
    - constantes.ENCABEZADO_FICHA
    - constantes.SECCION_COMENTARIOS
    - constantes.MSJ_SIN_COMENTARIOS
    - constantes.NOTA_PIE
    """
    with open("lead_app.py", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    constantes_faltantes = [
        "constantes.ENCABEZADO_FICHA",
        "constantes.SECCION_COMENTARIOS",
        "constantes.MSJ_SIN_COMENTARIOS",
        "constantes.NOTA_PIE"
    ]
    
    for const in constantes_faltantes:
        assert const not in contenido, \
            f"Aún existe referencia a {const} que no debería estar en lead_app.py"


def test_literales_españoles_en_ficha_tecnica():
    """
    Verifica que los literales en español estén presentes reemplazando las constantes.
    """
    with open("lead_app.py", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    literales_esperados = [
        "Información Pública del Emprendimiento",
        "Comentarios y Reseñas",
        "No hay comentarios disponibles",
        "Esta información fue recopilada automáticamente"
    ]
    
    for literal in literales_esperados:
        assert literal in contenido, \
            f"El literal '{literal}' no se encuentra en lead_app.py"


def test_scroll_configurado_en_ficha_tecnica():
    """
    Verifica que el scroll de la ventana de ficha técnica esté correctamente configurado
    usando el método `bind_all` y que se limpie al cerrar, como en la versión anterior.
    """
    with open("lead_app.py", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    # Extraer solo el contenido de la función `mostrar_info_detallada` para un análisis más preciso
    try:
        inicio = contenido.index("def mostrar_info_detallada(self, nombre, datos):")
        fin = contenido.index("def create_info_row(self, parent, label, value):")
        contenido_funcion = contenido[inicio:fin]
    except ValueError:
        contenido_funcion = contenido # Fallback a todo el archivo si no se encuentra

    # 1. Verificar que se usa bind_all para el scroll
    assert 'canvas.bind_all("<MouseWheel>", _on_mousewheel)' in contenido_funcion, \
        "Debe usarse 'canvas.bind_all' para el evento MouseWheel en la ficha técnica."
    
    # 2. Verificar que se define un handler on_close y se usa para limpiar el evento
    assert "def on_close():" in contenido_funcion, "Debe existir una función 'on_close'."
    assert 'canvas.unbind_all("<MouseWheel>")' in contenido_funcion, "Se debe llamar a 'canvas.unbind_all' al cerrar."
    assert 'top.protocol("WM_DELETE_WINDOW", on_close)' in contenido_funcion, "El protocolo de cierre debe llamar a on_close."
    
    # 3. Verificar que la lógica de límites YA NO está presente
    assert "canvas.yview()[0] <= 0.0" not in contenido_funcion, "La lógica de límite superior no debería estar presente."
    assert "canvas.yview()[1] >= 1.0" not in contenido_funcion, "La lógica de límite inferior no debería estar presente."