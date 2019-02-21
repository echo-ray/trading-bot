from core import float_to_str
from feeds.feed import Feed
from bittrex_websocket import BittrexSocket, BittrexMethods
from api.bittrex import normalize_pair, DELTA_TYPE_ADD, DELTA_TYPE_REMOVE
from pprint import pprint
import sys


class BittrexFeed(Feed, BittrexSocket):
    def feed(self, pair):
        self.depth_update_with_delta = True
        self.pair = normalize_pair(pair)
        tickers = [self.pair]
        self.query_exchange_state(tickers)
        self.subscribe_to_exchange_deltas(tickers)

    async def on_public(self, msg):
        if msg["invoke_type"] == BittrexMethods.QUERY_EXCHANGE_STATE:
            self.process_message(msg)

        if msg["invoke_type"] == BittrexMethods.SUBSCRIBE_TO_EXCHANGE_DELTAS:
            self.process_message(msg)

        if msg["invoke_type"] == BittrexMethods.QUERY_SUMMARY_STATE:
            self.process_message(msg)

        if msg["invoke_type"] == BittrexMethods.SUBSCRIBE_TO_SUMMARY_DELTAS:
            self.process_message(msg)

    def process_message(self, msg):
        self.process_depth_message(msg)

    def bids_from_msg(self, msg):
        return msg["Z"]

    def asks_from_msg(self, msg):
        return msg["S"]

    def on_summary_state(self, msg):
        market = self.find_market(msg, "s")
        self.emit_event(market)

    def on_summary_delta(self, msg):
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

    def ask_bid_volume(self, depth_item):
        return float(depth_item["Q"])

    def ask_bid_deleted(self, depth_item):
        return depth_item['TY'] == DELTA_TYPE_REMOVE

    def ask_bid_price(self, ask_bid):
        return float(ask_bid["R"])
