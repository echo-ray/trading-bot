from binance.websockets import BinanceSocketManager

from core import float_to_str
from feeds.feed import Feed
from api.binance import create_ws, normalize_pair
import sys
from pprint import pprint


class BinanceFeed(Feed):
    def feed(self, pair):
        bm = create_ws()
        bm.start_depth_socket(normalize_pair(pair), self.process_message, depth=BinanceSocketManager.WEBSOCKET_DEPTH_20)
        bm.daemon = True
        bm.start()
        return bm

    def process_message(self, msg):
        self.process_depth_message(msg)

    def process_depth_message(self, payload):
        sell_empty = float(0)
        buy_empty = float(sys.maxsize)
        sell = self.reduce_depth([sell_empty] + payload["bids"], None)
        buy = self.reduce_depth(None, [buy_empty] + payload["asks"])
        if not sell == sell_empty and not buy == buy_empty:
            msg = {
                "price": {
                    "sell": float_to_str(sell),
                    "buy": float_to_str(buy),
                }
            }
            self.e(msg)

    def process_ticker_message(self, payload):
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
