from feeds.feed import Feed
from api.okex.websocket import OkexWebSocket
import sys


class OkexFeed(Feed):
    def feed(self, pair):
        ws = OkexWebSocket(pair)
        ws.subscribe_to_feed(self.process_message)

    def process_message(self, payload):
        data = payload["data"][0]
        msg = {
            "price": {
                "sell": self.reduce_depth(["0"] + data["bids"], None),
                "buy": self.reduce_depth(None, [str(sys.maxsize)] + data["asks"]),
            }
        }
        self.e(msg)
