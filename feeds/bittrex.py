from feeds.feed import Feed
from bittrex_websocket import BittrexSocket, BittrexMethods
from api.bittrex import normalize_pair
from pprint import pprint


class BittrexFeed(Feed, BittrexSocket):
    def feed(self, pair):
        self.pair = normalize_pair(pair)
        tickers = [self.pair]
        self.query_summary_state()
        self.subscribe_to_summary_deltas()

    async def on_public(self, msg):
        if msg["invoke_type"] == BittrexMethods.QUERY_SUMMARY_STATE:
            self.on_query(msg)

        if msg["invoke_type"] == BittrexMethods.SUBSCRIBE_TO_SUMMARY_DELTAS:
            self.on_delta(msg)

    def on_query(self, msg):
        market = self.find_market(msg, "s")
        self.emit_event(market)

    def on_delta(self, msg):
        market = self.find_market(msg, "D")
        if market:
            self.emit_event(market)

    def emit_event(self, market):
        self.e({
            "price": {
                "sell": market["B"],
                "buy": market["A"]
            }
        })

    def find_market(self, msg, field):
        found = [x for x in msg[field] if x["M"] == self.pair]
        if len(found):
            return found[0]

        return None
