from binance.websockets import BinanceSocketManager
from feeds.feed import Feed
from api.binance import create_ws, normalize_pair
import sys


class BinanceFeed(Feed):
    def feed(self, pair):
        bm = create_ws()
        bm.start_depth_socket(normalize_pair(pair), self.process_message, depth=BinanceSocketManager.WEBSOCKET_DEPTH_10)
        bm.daemon = True
        bm.start()
        return bm

    def process_message(self, payload):
        sell_empty = "0"
        buy_empty = str(sys.maxsize)
        sell = self.reduce_depth([sell_empty] + payload["bids"], None)
        buy = self.reduce_depth(None, [buy_empty] + payload["asks"])
        if not sell == sell_empty and not buy == buy_empty:
            msg = {
                "price": {
                    "sell": sell,
                    "buy": buy,
                }
            }
            self.e(msg)
