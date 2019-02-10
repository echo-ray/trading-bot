from feeds.feed import Feed
from api.binance import create_ws, normalize_pair


class BinanceFeed(Feed):
    def feed(self, pair):
        self.pair = pair
        bm = create_ws()
        bm.start_miniticker_socket(self.process_message, 3000)
        bm.daemon = True
        bm.start()
        return bm

    def process_message(self, payload):
        el = [x for x in payload if x['s'] == normalize_pair(self.pair)]
        if len(el) > 0:
            msg = {
                'payload': payload,
                'price': el[0]["c"]
            }
            self.e(msg)
