from src.scraper import Scraper

class DummyDriver:
    def __init__(self):
        self.last_url = None
    def get(self, url):
        self.last_url = url


def test_navigate_to_maps_constructs_query():
    sc = Scraper()
    driver = DummyDriver()
    sc.navigate_to_maps(driver, "cafeterias")
    assert driver.last_url is not None
    assert "cafeterias" in driver.last_url
    assert "https://www.google.com/maps/search/" in driver.last_url
