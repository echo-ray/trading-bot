from lib.config import Config
from lib.event import Event
from core import calculate_remains


class Client(Config):
    def __init__(self, real, balance, pair):
        self.balance = balance
        self.real = real
        self.e = Event()
        self.pair = pair

    def get_balance(self, asset):
        return self.balance[asset]

    def get_fee(self, pair, buy):
        raise Exception("get_fee should be overwritten in particular client class")

    def calculate_fake_balance(self, pair, buy, price, quantity):
        fee = self.get_fee(pair, buy)
        self.balance = {
            **self.balance,
            **calculate_remains(pair, buy, price, quantity, fee, self.balance)
        }
