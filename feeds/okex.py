from feeds.feed import Feed
from api.okex.websocket import OkexWebSocket


class OkexFeed(Feed):
    def feed(self, pair):
        self.pair = pair
        ws = OkexWebSocket(pair)
        ws.subscribe_to_feed(self.process_message)

    def process_message(self, payload):
        # print("------------------------------------------------------------")
        # print(payload)
        # print("------------------------------------------------------------")
        msg = {
            'payload': payload[0]['data'],
            'price': payload[0]['data']['last']
        }
        self.e(msg)
