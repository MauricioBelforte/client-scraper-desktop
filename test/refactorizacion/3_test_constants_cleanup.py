import src.constants as constantes
import pytest


def test_ui_texts_removed():
    # tras la decisión de dejar literales en el código, estos atributos no deben existir
    for name in [
        'TITULO_APP','TEXTO_ENCABEZADO','TITULO_FRAME_BUSQUEDA','ETIQUETA_NUEVA_BUSQUEDA',
        'BTN_BUSCAR','BTN_MODO_RAPIDO','BTN_MODO_HUMANO','BTN_ENRIQUECER',
        'ETIQUETA_CARGAR_ARCHIVO','BTN_CARGAR','ETIQUETA_RESULTADOS',
        'COLUMNA_NOMBRE','COLUMNA_ESTADO','TEXTO_PLACEHOLDER_CARD',
        'ESTADO_LISTO','ENCABEZADO_CARD','ETIQUETA_TELEFONO','ETIQUETA_WEB',
        'ETIQUETA_CIUDAD','VALOR_SIN_WEB','VALOR_CIUDAD',
        'BTN_CONTACTAR_TODOS','BTN_VER_FICHA','BTN_BUSCAR_GOOGLE',
        'ENCABEZADO_FICHA','SECCION_COMENTARIOS','MSJ_SIN_COMENTARIOS'
    ]:
        assert not hasattr(constantes, name), f"{name} debería haberse eliminado de constants"
