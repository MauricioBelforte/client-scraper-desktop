import pytest
from src.scraper import Scraper


def test_get_chrome_options_exists_and_basic():
    sc = Scraper()
    # debe tener el método
    assert hasattr(sc, '_get_chrome_options'), "Falta método _get_chrome_options"
    options = sc._get_chrome_options()
    # opciones deben ser objeto selenium.options.Options o similar
    from selenium.webdriver.chrome.options import Options
    assert isinstance(options, Options)
    # comprobar que incluya al menos la localización es-419 si se implementa
    args = options.arguments
    assert any('--lang=es-419' in arg for arg in args), "Opciones deberían incluir lang=es-419"
