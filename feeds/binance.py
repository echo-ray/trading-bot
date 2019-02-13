from binance.websockets import BinanceSocketManager
from feeds.feed import Feed
from api.binance import create_ws, normalize_pair
import sys


class BinanceFeed(Feed):
    def feed(self, pair):
        bm = create_ws()
        bm.start_depth_socket(normalize_pair(pair), self.process_message, depth=BinanceSocketManager.WEBSOCKET_DEPTH_20)
        bm.daemon = True
        bm.start()
        return bm

    def process_message(self, payload):
        msg = {
            "price": {
                "sell": self.reduce_depth(["0"] + payload["bids"], None),
                "buy": self.reduce_depth(None, [str(sys.maxsize)] + payload["asks"]),
            }
        }
        self.e(msg)
