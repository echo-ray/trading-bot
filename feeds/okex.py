from feeds.feed import Feed
from api.okex.websocket import OkexWebSocket
import sys
from pprint import pprint
from functools import reduce


class OkexFeed(Feed):
    def feed(self, pair):
        ws = OkexWebSocket(pair)
        ws.subscribe_to_feed(self.process_message)

    def process_message(self, payload):
        data = payload["data"]
        min_sell = self.min_depth(data['asks'])
        min_buy = self.min_depth(data['bids'])
        if min_buy and min_sell:
            buy = reduce(
                lambda acc, ask: acc if acc < ask['price'] and ask['totalSize'] > "0" else acc,
                [min_sell] + data['asks'],
            )
            sell = reduce(
                lambda acc, bid: acc if acc > bid['price'] and bid['totalSize'] > "0" else acc,
                [min_buy] + data['bids'],
            )
            msg = {
                "price": {
                    "sell": sell,
                    "buy": buy,
                }
            }
            self.e(msg)

    def min_depth(self, arr):
        for el in arr:
            if el['totalSize'] > self.min_qty:
                return el['price']
        return None
