from feeds.feed import Feed
from api.okex.websocket import OkexWebSocket
import sys
from pprint import pprint
from functools import reduce


class OkexFeed(Feed):
    def feed(self, pair):
        ws = OkexWebSocket(pair)
        ws.subscribe_to_feed(self.process_message)

    def process_message(self, msg):
        self.process_depth_message(msg)

    def process_depth_message(self, payload):
        data = payload["data"]
        if len(data):
            depth = data[0]
            empty_sell = float(0)
            empty_buy = float(sys.maxsize)
            sell = self.reduce_depth(
                [empty_sell] + depth["bids"],
                None
            )
            buy = self.reduce_depth(
                None,
                [empty_buy] + depth["asks"]
            )
            if not buy == empty_buy and not sell == empty_sell:
                self.e(
                    {
                        "price": {
                            "buy": str(buy),
                            "sell": str(sell)
                        }
                    }
                )

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
