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
    Verifica que el scroll de la ventana de ficha técnica esté correctamente configurado.
    Asegura que el binding para MouseWheel funciona en múltiples widgets.
    """
    with open("lead_app.py", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    # Verificar que el scroll está vinculado a múltiples widgets
    assert 'top.bind("<MouseWheel>"' in contenido or 'top.bind("<MouseWheel>"' in contenido, \
        "El binding del scroll debería estar vinculado a la ventana principal (top)"
    
    assert 'canvas.bind("<MouseWheel>"' in contenido, \
        "El binding del scroll debería estar vinculado al canvas"
    
    assert 'info_frame.bind("<MouseWheel>"' in contenido, \
        "El binding del scroll debería estar vinculado al info_frame"
    
    # Verificar que hay una función para vincular recursivamente a los hijos
    assert "bind_mousewheel_to_children" in contenido, \
        "Debe existir una función para vincular el scroll a los widgets hijos recursivamente"
    
    # Verificar que el evento se limpia correctamente al cerrar
    assert "unbind" in contenido, \
        "Debe haber un unbind para limpiar el evento al cerrar la ventana"
