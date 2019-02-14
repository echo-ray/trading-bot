from feeds.feed import Feed
from time import sleep
from bittrex_websocket import BittrexSocket
from pprint import pprint


class BittrexFeed(Feed, BittrexSocket):
    def feed(self, pair):
        self.pair = pair
        self.query_exchange_state([pair])

    async def on_public(self, msg):
        pprint(msg)
        self.query_exchange_state([self.pair])
