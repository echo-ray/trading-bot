from lib.event import Event
from lib.config import Config
from functools import reduce
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-qty", "--quantity", dest="quantity",
                    help="asset quantity to trade", default="1")

args, extra = parser.parse_known_args()


class Feed(Config):
    def __init__(self):
        super().__init__()
        self.e = Event()
        self.min_qty = float(args.quantity)

    def subscribe(self, cb):
        self.e.append(cb)

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
            return acc if float(acc) > price else price

        return acc

    def compare_ask(self, acc, ask):
        if self.check_volume(ask):
            price = self.ask_bid_price(ask)
            return acc if float(acc) < price else price

        return acc

    def check_volume(self, depth_item):
        return float(depth_item[1]) >= self.min_qty

    def ask_bid_price(self, ask_bid):
        return float(ask_bid[0])
