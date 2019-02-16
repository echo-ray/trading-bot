#!/usr/bin/python

from argparse import ArgumentParser
from feeds.binance import BinanceFeed
from feeds.okex import OkexFeed
from feeds.bittrex import BittrexFeed
from rx import Observable
import time
from lib.config import Config
from clients.binance import BinanceClient
from clients.okex import OkexClient
from clients.bittrex import BittrexClient
from termcolor import colored
import importlib
import sys
import os

parser = ArgumentParser()
parser.add_argument("-p", "--pair", dest="pair",
                    help="pair to trade")

parser.add_argument("-str", "--strategy", dest="strategy",
                    help="filename of the strategy", default="default")

parser.add_argument("-s", "--steps", dest="steps",
                    help="number of steps to execute", default=None, type=int)

parser.add_argument("-stp", "--current-step", dest="current_step",
                    help="current step to start")

parser.add_argument("-r", "--real", dest="real", action="store_true",
                    help="make real trades", default=False)

parser.add_argument("-log", "--log", dest="log", action="store_true",
                    help="log prices", default=False)

parser.add_argument('-exc', action='append', dest='exchanges',
                    default=[],
                    help='exchanges list',
                    )


args, extra = parser.parse_known_args()

feeds = {
    "binance": BinanceFeed,
    "okex": OkexFeed,
    "bittrex": BittrexFeed
}

clients = {
    "binance": BinanceClient,
    "okex": OkexClient,
    "bittrex": BittrexClient
}

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    os._exit(1)

config = Config()
balance = config.load_json("balance.json")

leftExc, rightExc = args.exchanges

leftClient = clients[leftExc](args.real, balance[leftExc], args.pair)
rightClient = clients[rightExc](args.real, balance[rightExc], args.pair)


class StateMachine:
    def __init__(self):
        strategy = importlib.import_module('strategies.' + args.strategy)
        self.transitions = strategy.transitions
        self.perform_step = strategy.perform_step
        if args.current_step:
            self.step = args.current_step
        else:
            self.step = next(iter(self.transitions))
        self.steps = 0
        leftClient.subscribe_to_order_filled(self.next)
        rightClient.subscribe_to_order_filled(self.next)

    def run(self, left_price, right_price):
        if self.steps == args.steps:
            os._exit(1)

        if args.log:
            print(colored("{} price: {} {} price: {}".format(leftExc, left_price, rightExc, right_price), 'cyan'))

        if self.perform_step(left_price, right_price, leftClient, rightClient, args.pair, self.step):
            self.next()

    def next(self):
        self.steps += 1
        print(
            colored("transition from {} to {} step".format(self.step, self.transitions[self.step]), "magenta")
        )
        self.step = self.transitions[self.step]


stateMachine = StateMachine()


def on_stream_value(v):
    left, right = v
    stateMachine.run(left['price'], right['price'])


def start_feed(Feed, onValue):
    feed = Feed()
    feed.subscribe(onValue)
    feed.feed(args.pair)


leftFeed = feeds[leftExc]
rightFeed = feeds[rightExc]

leftStream = Observable.create(lambda observer: start_feed(leftFeed, lambda value: observer.on_next(value)))
rightStream = Observable.create(lambda observer: start_feed(rightFeed, lambda value: observer.on_next(value)))

Observable.combine_latest(
    leftStream,
    rightStream,
    lambda l, r: (l, r)
).subscribe(on_stream_value)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("bot has been interrupted")
    os._exit(1)


