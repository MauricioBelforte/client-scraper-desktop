import pytest

from src import scraper


def test_clase_scraper_existe():
    # antes de refactorizar, el módulo puede no existir o estar vacío
    assert hasattr(scraper, 'Scraper'), "La clase Scraper debe estar definida en src/scraper.py"
    cls = getattr(scraper, 'Scraper')
    # debe ser instanciable sin argumentos
    instancia = cls(lambda msg: None)
    assert instancia is not None
