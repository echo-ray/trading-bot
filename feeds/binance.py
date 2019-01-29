from feeds.feed import Feed
from binance.enums import *
from api.binance import create_ws, normalize_pair


class BinanceFeed(Feed):
    def feed(self, pair):
        bm = create_ws()
        bm.start_kline_socket(normalize_pair(pair), self.process_message, interval=KLINE_INTERVAL_1DAY)
        bm.daemon = True
        bm.start()
        return bm

    def process_message(self, payload):
        msg = {
            'payload': payload,
            'price': payload['k']['c']
        }
        self.e(msg)
