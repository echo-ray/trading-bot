from core import float_to_str
from feeds.feed import Feed
from bittrex_websocket import BittrexSocket, BittrexMethods
from api.bittrex import normalize_pair, DELTA_TYPE_ADD
from pprint import pprint
import sys


class BittrexFeed(Feed, BittrexSocket):
    def feed(self, pair):
        self.pair = normalize_pair(pair)
        tickers = [self.pair]
        self.query_exchange_state(tickers)
        self.subscribe_to_exchange_deltas(tickers)

    async def on_public(self, msg):
        if msg["invoke_type"] == BittrexMethods.QUERY_EXCHANGE_STATE:
            self.on_exchange_state(msg)

        if msg["invoke_type"] == BittrexMethods.SUBSCRIBE_TO_EXCHANGE_DELTAS:
            self.on_exchange_state(msg)

        if msg["invoke_type"] == BittrexMethods.QUERY_SUMMARY_STATE:
            self.on_summary_state(msg)

        if msg["invoke_type"] == BittrexMethods.SUBSCRIBE_TO_SUMMARY_DELTAS:
            self.on_summary_delta(msg)

    def on_exchange_state(self, msg):
        sells = msg["S"]
        bids = msg["Z"]
        empty_sell = float(0)
        empty_buy = float(sys.maxsize)
        sell = self.reduce_depth(
            [empty_sell] + bids,
            None
        )
        buy = self.reduce_depth(
            None,
            [empty_buy] + sells
        )

        if not buy == empty_buy and not sell == empty_sell:
            self.e(
                {
                    "price": {
                        "buy": float_to_str(buy),
                        "sell": float_to_str(sell)
                    }
                }
            )

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

    def check_volume(self, depth_item):
        if 'TY' in depth_item:
            if not depth_item['TY'] == DELTA_TYPE_ADD:
                return False
        return float(depth_item["Q"]) >= self.min_qty

    def ask_bid_price(self, ask_bid):
        return float(ask_bid["R"])
