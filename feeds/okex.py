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
        sell_empty = 0
        buy_empty = sys.maxsize
        sell = self.reduce_depth([sell_empty] + data["bids"], None)
        buy = self.reduce_depth(None, [buy_empty] + data["asks"])
        if not sell == sell_empty and not buy == buy_empty:
            msg = {
                "price": {
                    "sell": sell,
                    "buy": buy,
                }
            }
            self.e(msg)

    def check_volume(self, depth_item):
        return float(depth_item["totalSize"]) >= self.min_qty

    def ask_bid_price(self, ask_bid):
        return float(ask_bid["price"])
