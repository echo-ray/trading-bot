from core import float_to_str
from lib.event import Event
from functools import reduce
import sys
from lib.config import Config
from pprint import pprint
import os
import json
from decimal import Decimal

args = Config.get_args()


class Feed(Config):
    def __init__(self):
        super().__init__()
        self.e = Event()
        self.min_qty = float(args.quantity)
        self.process_depth_message = self.process_full_depth_message
        self.pair = None
        self.bids = []
        self.asks = []
        self.best_bid = None
        self.best_ask = None
        self.sell_empty = float(0)
        self.buy_empty = float(sys.maxsize)
        self.depth_update_with_delta = False

    def subscribe(self, cb):
        self.e.append(cb)

    def unsubscribe(self, cb):
        self.e.remove(cb)

    def bids_from_msg(self, msg):
        raise Exception("feed should implement bids_from_msg")

    def asks_from_msg(self, msg):
        raise Exception("feed should implement asks_from_msg")

    def process_full_depth_message(self, msg):
        if self.depth_update_with_delta:
            self.process_depth_message = self.process_delta_depth_message

        bids = self.bids_from_msg(msg)
        asks = self.asks_from_msg(msg)

        self.bids = bids
        self.asks = asks

        self.emit_from_full_depth(bids, asks)

    def process_delta_depth_message(self, msg):
        bids = self.bids_from_msg(msg)
        asks = self.asks_from_msg(msg)

        for ask in asks:
            if self.ask_bid_deleted(ask):
                try:
                    self.asks.remove(ask)
                except Exception:
                    pass

                if self.ask_bid_price(ask) == self.best_ask:
                    self.best_ask = self.buy_empty
            else:
                self.asks.append(ask)
                self.best_ask = self.compare_ask(self.best_ask, ask)

        for bid in bids:
            if self.ask_bid_deleted(bid):
                try:
                    self.bids.remove(bid)
                except Exception:
                    pass

                if self.ask_bid_price(bid) == self.best_bid:
                    self.best_bid = self.sell_empty
            else:
                self.bids.append(bid)
                self.best_bid = self.compare_bid(self.best_bid, bid)

        self.emit_from_depth()

    def emit_from_full_depth(self, bids, asks):
        sell = self.reduce_depth([self.sell_empty] + bids, None)
        buy = self.reduce_depth(None, [self.buy_empty] + asks)

        self.best_bid = sell
        self.best_ask = buy

        self.emit_from_depth()

    def emit_from_delta(self):
        if self.best_ask == self.buy_empty:
            self.best_ask = self.reduce_depth(None, [self.buy_empty] + self.asks)

        if self.best_bid == self.sell_empty:
            self.best_bid = self.reduce_depth([self.sell_empty] + self.bids, None)

        self.emit_from_depth()

    def emit_from_depth(self):
        if not self.best_bid == self.sell_empty and not self.best_ask == self.buy_empty:
            msg = {
                "price": {
                    "sell": float_to_str(self.best_bid),
                    "buy": float_to_str(self.best_ask),
                }
            }
            self.e(msg)

    def reduce_depth(self, bids, asks):
        if bids:
            return reduce(
                self.compare_bid,
                bids
            )

        if asks:
            return reduce(
                self.compare_ask,
                asks
            )

    def compare_bid(self, acc, bid):
        if self.check_volume(bid):
            price = self.ask_bid_price(bid)
            return acc if Decimal(acc) > price else price

        return acc

    def compare_ask(self, acc, ask):
        if self.check_volume(ask):
            price = self.ask_bid_price(ask)
            return acc if Decimal(acc) < price else price

        return acc

    def filter_empty_ask_bids(self, depth_items):
        return list(
            filter(
                lambda item: not self.ask_bid_deleted(item),
                depth_items
            )
        )

    def ask_bid_deleted(self, depth_item):
        raise Exception("ask_bid_deleted should be implemented in particular feed")

    def ask_bid_volume(self, depth_item):
        return Decimal(depth_item[1])

    def check_volume(self, depth_item):
        return self.ask_bid_volume(depth_item) > self.min_qty

    def ask_bid_price(self, ask_bid):
        return Decimal(ask_bid[0])
