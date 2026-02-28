import pytest
from src.utilidades import create_whatsapp_url


@pytest.mark.parametrize("nombre, input_tel, expected_in_url", [
    ("Juan", "0280123456", "549280123456"),          # Caso original: Elimina 0 inicial
    ("Maria", "280154123456", "5492804123456"),       # Nuevo: Elimina 15 intermedio
    ("Pedro", "0280-15-4123456", "5492804123456"),    # Nuevo: Elimina 0, 15 y guiones
    ("Ana", "(280) 412-3456", "5492804123456"),       # Nuevo: Elimina paréntesis y guiones
    ("Luis", "+5492804123456", "5492804123456"),      # Caso: Número ya correcto
    ("Laura", "Sin Telefono", None),                 # Caso: Sin teléfono no debe generar URL
])
def test_create_whatsapp_url_argentina_formats(nombre, input_tel, expected_in_url):
    """
    Verifica que la función create_whatsapp_url maneje varios formatos de
    números argentinos, limpiando prefijos locales (0, 15) y caracteres.
    """
    url = create_whatsapp_url(nombre, input_tel)
    
    if expected_in_url is None:
        assert url is None, "La función debería devolver None para entradas inválidas"
    else:
        assert url is not None, "La URL no debería ser None para una entrada válida"
        assert expected_in_url in url, f"El número esperado {expected_in_url} no está en la URL {url}"
        assert url.startswith("https://wa.me/")
