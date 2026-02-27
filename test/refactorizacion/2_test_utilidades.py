import pytest
from src.utilidades import create_whatsapp_url


def test_create_whatsapp_url_argentina_formats():
    # varios formatos de entrada deben producir url válida con prefijo 549
    url = create_whatsapp_url("Juan", "0280123456")
    assert "549280123456" in url
    assert url.startswith("https://wa.me/")
