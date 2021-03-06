from clients.client import Client
from api.okex.account_api import AccountAPI
from api.okex.spot_api import SpotAPI
from api.okex.credentials import api_key, pass_phrase, secret_key
from functools import reduce
from api.okex.consts import *
from api.okex.websocket import OkexWebSocket
import threading
from core import split_pair, float_to_str
import os
from decimal import Decimal


class OkexClient(Client):
    def __init__(self, *args):
        Client.__init__(self, *args)
        self.account_api = AccountAPI(api_key, secret_key, pass_phrase, True)
        self.spot_api = SpotAPI(api_key, secret_key, pass_phrase, True)
        fees_arr = self.account_api.get_coin_fee()
        self.fees = reduce(
            lambda acc, curr: {**acc, '' + curr['currency']: curr},
            [{}] + fees_arr
        )
        self.current_order_id = None
        self.on_order_filled = lambda: None
        self.ws = None
        self.exchange = "okex"

    def on_order_update(self, msg):
        status = msg['data'][0]['status']
        order_id = msg['data'][0]['order_id']
        if order_id == self.current_order_id:
            if status == ORDER_FILLED:
                self.calculate_new_balance(
                    msg,
                    self.pair
                )
                self.on_order_filled()

            if status == ORDER_CANCELLED or status == ORDER_FAILURE:
                print("okex order: {} finished with error".format_map(self.current_order_id))
                os._exit(1)

    def subscribe_to_order_filled(self, cb):
        self.on_order_filled = cb

    def get_fee(self, pair, buy):
        return 0.0015

    def get_step_size(self, pair):
        return '0.01000000'

    def buy(self, price, count, pair):
        if self.real:
            return self.real_order(
                price,
                count,
                pair,
                SIDE_BUY
            )
        return self.fake_order(
            price,
            count,
            pair,
            SIDE_BUY
        )

    def sell(self, price, count, pair):
        if self.real:
            return self.real_order(
                price,
                count,
                pair,
                SIDE_SELL
            )
        return self.fake_order(
            price,
            count,
            pair,
            SIDE_SELL
        )

    def real_order(self, price, count, pair, side):
        resp = self.spot_api.take_order(
            ORDER_TYPE_LIMIT,
            side,
            pair,
            count,
            price
        )
        if resp['result']:
            self.current_order_id = resp["order_id"]
            if not self.ws:
                self.ws = OkexWebSocket(pair)
                self.ws.subscribe_to_order_update(self.on_order_update)

            if not resp['result']:
                print("okex order failed: {}".format(resp))

            return resp['result']
        else:
            raise Exception(resp)

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

    def calculate_new_balance(self, order, pair, buy=None, price=None, quantity=None):
        if order:
            asset, quote = split_pair(pair)
            asset_wallet = self.account_api.get_currency(asset)
            quote_wallet = self.account_api.get_currency(quote)
            self.balance[asset] = asset_wallet[0]['available']
            self.balance[quote] = quote_wallet[0]['available']
        else:
            self.calculate_fake_balance(pair, buy, price, quantity)
