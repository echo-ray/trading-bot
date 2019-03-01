from core import float_to_str
from feeds.feed import Feed
from api.okex.websocket import OkexWebSocket
import sys
from pprint import pprint


class OkexFeed(Feed):
    def feed(self, pair):
        self.depth_update_with_delta = True
        ws = OkexWebSocket(pair)
        ws.subscribe_to_feed(self.process_message)

    def process_message(self, msg):
        self.process_depth_message(msg)

    def bids_from_msg(self, payload):
        data = payload["data"]
        if len(data):
            depth = data[0]
            return depth["bids"]

    def asks_from_msg(self, payload):
        data = payload["data"]
        if len(data):
            depth = data[0]
            return depth["asks"]

    def process_ticker_message(self, payload):
        data = payload["data"]
        if len(data):
            ticker = data[0]
            bid_price = ticker["best_bid"]
            ask_price = ticker["best_ask"]
            self.e(
                {
                    "price": {
                        "buy": ask_price,
                        "sell": bid_price,
                    }
                }
            )

    def ask_bid_deleted(self, depth_item):
        return float(depth_item[2]) == 0
