from clients.client import Client
from binance.enums import *
from api.binance import create_client, normalize_pair, get_fees, create_ws
from functools import reduce
from core import split_pair
import threading


class BinanceClient(Client):
    def __init__(self, *args):
        Client.__init__(self, *args)
        client = create_client()
        self.client = client
        fees_arr = get_fees()
        self.fees = reduce(
            lambda acc, curr: {**acc, '' + curr['symbol']: curr},
            [{}] + fees_arr
        )
        self.exchange = "binance"

        self.last_order_id = None
        ws = create_ws()
        ws.start_user_socket(self.on_user_socket_msg)
        ws.daemon = True
        ws.start()
        self.on_order_filled = lambda: None

    def subscribe_to_order_filled(self, cb):
        self.on_order_filled = cb

    def on_user_socket_msg(self, msg):
        if msg["e"] == "executionReport":
            if msg["c"] == self.last_order_id:
                if msg["X"] == ORDER_STATUS_FILLED:
                    self.calculate_new_balance(
                        msg,
                        self.pair,
                    )
                    self.on_order_filled()
                if msg["X"] == ORDER_STATUS_CANCELED or msg["X"] == ORDER_STATUS_REJECTED:
                    raise Exception("binance order finished with error {}".format(msg["r"]))

    def get_fee(self, pair, buy):
        return self.fees[normalize_pair(pair)]['taker']

    def get_symbol_info(self, pair):
        return self.client.get_symbol_info(normalize_pair(pair))

    def buy(self, price, count, pair):
        if self.real:
            return self.real_order(price, count, pair, SIDE_BUY)
        else:
            return self.fake_order(price, count, pair, SIDE_BUY)

    def sell(self, price, count, pair):
        if self.real:
            return self.real_order(price, count, pair, SIDE_SELL)
        else:
            return self.fake_order(price, count, pair, SIDE_SELL)

    def real_order(self, price, count, pair, side):
        order = self.client.create_order(
            symbol=normalize_pair(pair),
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=count,
            price=price,
            newOrderRespType=ORDER_RESP_TYPE_RESULT
        )
        status = order["status"]
        success = status != ORDER_STATUS_CANCELED and status != ORDER_STATUS_REJECTED
        if success:
            if status == ORDER_STATUS_FILLED:
                self.last_order_id = None
                self.tick_order_filled()
            else:
                self.last_order_id = order["clientOrderId"]
        else:
            print("binance order failed: {}".format(order))

        return success

    def fake_order(self, price, count, pair, side):
        self.client.create_test_order(
            symbol=normalize_pair(pair),
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=count,
            price=price,
            newOrderRespType=ORDER_RESP_TYPE_RESULT
        )
        self.calculate_new_balance(
            None,
            pair,
            side == SIDE_BUY,
            price,
            count
        )
        self.tick_order_filled()
        return True

    def tick_order_filled(self):
        t = threading.Timer(0.1, self.on_order_filled)
        t.start()

    def calculate_new_balance(self, order, pair, buy=None, price=None, quantity=None):
        if order:
            asset, quote = split_pair(pair)
            asset_wallet = self.client.get_asset_balance(asset=asset)
            quote_wallet = self.client.get_asset_balance(asset=quote)
            self.balance[asset] = asset_wallet['free']
            self.balance[quote] = quote_wallet['free']
        else:
            self.calculate_fake_balance(pair, buy, price, quantity)
