from argparse import ArgumentParser
from feeds.binance import BinanceFeed
from feeds.okex import OkexFeed
from feeds.bittrex import BittrexFeed
from termcolor import colored
import os
import sys
import time

parser = ArgumentParser()
parser.add_argument("-f", "--feed", dest="feed",
                    help="feed adapter")
parser.add_argument("-p", "--pair", dest="pair",
                    help="pair to get feed on")

args, extra = parser.parse_known_args()

feeds = {
    "okex": OkexFeed,
    "binance": BinanceFeed,
    "bittrex": BittrexFeed,
}

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
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
