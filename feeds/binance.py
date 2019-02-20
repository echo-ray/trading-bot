from feeds.feed import Feed
from api.binance import create_ws, normalize_pair
import sys
from pprint import pprint


class BinanceFeed(Feed):
    def feed(self, pair):
        bm = create_ws()
        bm.start_symbol_ticker_socket(normalize_pair(pair), self.process_message)
        bm.daemon = True
        bm.start()
        return bm

    def process_message(self, payload):
        bid_price = payload["b"]
        bid_quantity = payload["B"]
        ask_price = payload["a"]
        ask_quantity = payload["A"]

        if float(bid_quantity) >= self.min_qty and float(ask_quantity) >= self.min_qty:
            self.e(
                {
                    "price": {
                        "buy": ask_price,
                        "sell": bid_price,
                    }
                }
            )
