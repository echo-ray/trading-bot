from clients.client import Client
from binance.enums import *
from api.binance import create_client, normalize_pair, get_fees
from functools import reduce
from core import split_pair


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
            timeInForce=TIME_IN_FORCE_FOK,
            quantity=count,
            price=price,
            newOrderRespType=ORDER_RESP_TYPE_RESULT
        )
        success = order["status"] == ORDER_STATUS_FILLED
        if success:
            self.calculate_new_balance(
                order,
                pair,
                side == SIDE_BUY,
                price,
                count
            )
        return success

    def fake_order(self, price, count, pair, side):
        self.client.create_test_order(
            symbol=normalize_pair(pair),
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_FOK,
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
        return True

    def calculate_new_balance(self, order, pair, buy, price, quantity):
        if order:
            asset, quote = split_pair(pair)
            asset_wallet = self.client.get_asset_balance(asset=asset)
            quote_wallet = self.client.get_asset_balance(asset=quote)
            self.balance[asset] = asset_wallet['free']
            self.balance[quote] = quote_wallet['free']
        else:
            self.calculate_fake_balance(pair, buy, price, quantity)
