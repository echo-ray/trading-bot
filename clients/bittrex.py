from clients.client import Client
from bittrex.bittrex import *
from api.bittrex import normalize_pair
from apscheduler.schedulers.background import BackgroundScheduler
import threading
from core import split_pair

SIDE_BUY = "SIDE_BUY"
SIDE_SELL = "SIDE_SELL"


class BittrexClient(Client):
    def __init__(self, *args):
        super().__init__(*args)
        creds = self.credentials("bittrex.json")
        self.api = Bittrex(creds["apiKey"], creds["secret"])
        self.last_order_id = None
        self.on_order_filled = lambda: None
        self.scheduler = None
        self.exchange = "bittrex"

    def get_fee(self, pair, buy):
        # 0.25%
        return 0.0025

    def get_step_size(self, pair):
        return '0.01000000'

    def subscribe_to_order_filled(self, cb):
        self.on_order_filled = cb

    def buy(self, price, count, pair):
        if self.real:
            result = self.api.buy_limit(
                normalize_pair(pair),
                count,
                price
            )
            return self.from_real_order(result)

        return self.fake_order(price, count, pair, SIDE_BUY)

    def sell(self, price, count, pair):
        if self.real:
            result = self.api.sell_limit(
                normalize_pair(pair),
                count,
                price
            )
            return self.from_real_order(result)

        return self.fake_order(price, count, pair, SIDE_SELL)

    def from_real_order(self, result):
        success = result["success"]
        if success:
            self.last_order_id = result["result"]["uuid"]
            self.wait_for_order_execution()

        return success

    def fake_order(self, price, count, pair, side):
        self.calculate_new_balance(
            None,
            pair,
            side == SIDE_BUY,
            price,
            count,
        )
        t = threading.Timer(0.1, self.on_order_filled)
        t.start()
        return True

    def wait_for_order_execution(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.check_order_status, 'interval', seconds=1)
        self.scheduler.start()

    def check_order_status(self):
        resp = self.api.get_order(self.last_order_id)
        result = resp["result"]
        if "Closed" in result:
            if isinstance(result["Closed"], str):
                self.last_order_id = None
                self.scheduler.shutdown()
                self.on_order_filled()

    def calculate_new_balance(self, order, pair, buy=None, price=None, quantity=None):
        if order:
            asset, quote = split_pair(pair)
            resp = self.api.get_balances()
            balances = resp["result"]
            quote_wallet = [x for x in balances if x["Currency"] == quote][0]
            asset_wallet = [x for x in balances if x["Currency"] == asset][0]
            self.balance[asset] = asset_wallet["Available"]
            self.balance[quote] = quote_wallet["Available"]
        else:
            self.calculate_fake_balance(pair, buy, price, quantity)
