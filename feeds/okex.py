from feeds.feed import Feed
from api.okex.websocket import OkexWebSocket


class OkexFeed(Feed):
    def feed(self, pair):
        ws = OkexWebSocket(pair)
        ws.subscribe_to_feed(self.process_message)

    def process_message(self, payload):
        msg = {
            'payload': payload,
            'price': payload['data'][0]['price']
        }
        self.e(msg)
