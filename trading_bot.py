#!/usr/bin/python

from feeds.binance import BinanceFeed
from feeds.okex import OkexFeed
from feeds.bittrex import BittrexFeed
import time
from lib.config import Config
from clients.binance import BinanceClient
from clients.okex import OkexClient
from clients.bittrex import BittrexClient
from termcolor import colored
import importlib
import sys
import os
from lib.state_machine import StateMachine
from lib.combiner import Combiner

args = Config.get_args()

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
    Config.print_help(sys.stderr)
    os._exit(1)

config = Config()
balance = config.load_json("balance.json")

leftExc, rightExc = args.exchanges

leftClient = clients[leftExc](args.real, balance[leftExc], args.pair)
rightClient = clients[rightExc](args.real, balance[rightExc], args.pair)


strategy = importlib.import_module('strategies.' + args.strategy)
transitions = strategy.transitions
stateMachine = StateMachine(
    strategy,
    args.current_step if args.current_step else next(iter(transitions))
)
leftClient.subscribe_to_order_filled(stateMachine.next)
rightClient.subscribe_to_order_filled(stateMachine.next)


def on_stream_value(v):
    left, right = v
    left_price = left['price']
    right_price = right['price']

    if stateMachine.steps == args.steps:
        os._exit(1)

    if args.log:
        print(colored("{} price: {} {} price: {}".format(leftExc, left_price, rightExc, right_price), 'cyan'))

    if strategy.perform_step(left_price, right_price, leftClient, rightClient, args.pair, stateMachine.step):
        stateMachine.next()


def start_feed(Feed, onValue):
    feed = Feed()
    feed.subscribe(onValue)
    feed.feed(args.pair)


leftFeed = feeds[leftExc]
rightFeed = feeds[rightExc]


combiner = Combiner(on_stream_value, args.combiner_log)
start_feed(leftFeed, combiner.on_left)
start_feed(rightFeed, combiner.on_right)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("bot has been interrupted")
    os._exit(1)


