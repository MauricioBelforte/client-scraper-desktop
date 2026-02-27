import pytest
from src.scraper import Scraper

class DummyDriver:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class DummyDMManager:
    def install(self):
        return '/fake/chromedriver/path'

def test_initialize_driver_invokes_webdriver(monkeypatch):
    sc = Scraper()
    called = {}
    
    def fake_chrome(*args, **kwargs):
        called['args'] = args
        called['kwargs'] = kwargs
        return DummyDriver()
    
    # Mock both webdriver.Chrome and ChromeDriverManager
    monkeypatch.setattr('src.scraper.webdriver.Chrome', fake_chrome)
    monkeypatch.setattr('src.scraper.ChromeDriverManager', DummyDMManager)
    
    # call the method
    driver = sc._initialize_driver()
    assert isinstance(driver, DummyDriver)
    # ensure Options were passed via named param 'options'
    assert 'options' in called['kwargs']
    from selenium.webdriver.chrome.options import Options
    assert isinstance(called['kwargs']['options'], Options)
