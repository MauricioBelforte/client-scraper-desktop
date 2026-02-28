import src.constants as constantes

def test_rubros_list_not_empty():
    assert constantes.RUBROS_SUGERIDOS, "La lista de rubros sugeridos no debe estar vacía"
