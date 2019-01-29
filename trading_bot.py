#!/usr/bin/python

from argparse import ArgumentParser
from feeds.binance import BinanceFeed
from feeds.okex import OkexFeed
from rx import Observable
import time
from lib.config import Config
from clients.binance import BinanceClient
from clients.okex import OkexClient
from termcolor import colored
import importlib
import sys

parser = ArgumentParser()
parser.add_argument("-p", "--pair", dest="pair",
                    help="pair to trade")

parser.add_argument("-str", "--strategy", dest="strategy",
                    help="filename of the strategy", default="default")

parser.add_argument("-s", "--steps", dest="steps",
                    help="number of steps to execute", default=None, type=int)

parser.add_argument("-r", "--real", dest="real", action="store_true",
                    help="make real trades", default=False)


args, extra = parser.parse_known_args()

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

config = Config()
balance = config.load_json("balance.json")

binanceClient = BinanceClient(args.real, balance['binance'])
okexClient = OkexClient(args.real, balance['okex'])


class StateMachine:
    def __init__(self):
        strategy = importlib.import_module('strategies.' + args.strategy)
        self.transitions = strategy.transitions
        self.perform_step = strategy.perform_step
        self.step = next(iter(self.transitions))
        self.steps = 0
        okexClient.subscribe_to_order_filled(self.next)

    def run(self, binance_price, okex_price):
        if self.steps == args.steps:
            sys.exit(1)

        print(colored("binance price: {} okex price: {}".format(binance_price, okex_price), 'cyan'))

        if self.perform_step(binance_price, okex_price, binanceClient, okexClient, args.pair, self.step):
            self.next()

    def next(self):
        self.steps += 1
        print(
            colored("transition from {} to {} step".format(self.step, self.transitions[self.step]), "magenta")
        )
        self.step = self.transitions[self.step]


stateMachine = StateMachine()


def on_stream_value(v):
    binance,okex = v
    stateMachine.run(binance['price'], okex['price'])


def start_feed(Feed, onValue):
    feed = Feed()
    feed.subscribe(onValue)
    feed.feed(args.pair)


binanceStream = Observable.create(lambda observer: start_feed(BinanceFeed, lambda value: observer.on_next(value)))
okexStream = Observable.create(lambda observer: start_feed(OkexFeed, lambda value: observer.on_next(value)))

Observable.zip(
    binanceStream,
    okexStream,
    lambda b, o: (b, o)
).subscribe(on_stream_value)

try:
    while True:
        time.sleep(0.1)
except Exception:
    print("bot has been interrupted")


