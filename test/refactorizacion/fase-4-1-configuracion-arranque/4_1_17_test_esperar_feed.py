from src.scraper import Scraper

class DummyWait:
    def __init__(self):
        self.called = False
        self.args = None
        self.kwargs = None
    def until(self, condition):
        self.called = True
        self.args = condition
        return True


def test_wait_for_feed_calls_until():
    sc = Scraper()
    wait = DummyWait()
    result = sc._wait_for_feed(wait)
    assert wait.called, "_wait_for_feed should call wait.until"
    # condition is expected to be an instance of some sentinel; we just check not None
    assert wait.args is not None
