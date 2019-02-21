from lib.config import Config
from feeds.binance import BinanceFeed
from feeds.okex import OkexFeed
from feeds.bittrex import BittrexFeed
from termcolor import colored
import os
import sys
import time

args = Config.get_args()

feeds = {
    "okex": OkexFeed,
    "binance": BinanceFeed,
    "bittrex": BittrexFeed,
}

if len(sys.argv) == 1:
    Config.print_help(sys.stderr)
    os._exit(1)


def on_value(value):
    print(colored("{} price: {}".format(args.feed, value['price']), "cyan"))


feed = feeds[args.feed]()
feed.subscribe(on_value)
feed.feed(args.pair)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    os._exit(1)
