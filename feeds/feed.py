from lib.event import Event
from lib.config import Config

class Feed(Config):
    def __init__(self):
        self.e = Event()

    def subscribe(self, cb):
        self.e.append(cb)