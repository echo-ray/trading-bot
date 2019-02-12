from argparse import ArgumentParser
from feeds.binance import BinanceFeed
from feeds.okex import OkexFeed
from termcolor import colored
import os
import sys
import time
import threading, queue
from lib.selenium import create_driver, draw_on_screen

parser = ArgumentParser()
parser.add_argument("-f", "--feed", dest="feed",
                    help="feed adapter")
parser.add_argument("-p", "--pair", dest="pair",
                    help="pair to get feed on")

args, extra = parser.parse_known_args()

feeds = {
    "okex": OkexFeed,
    "binance": BinanceFeed,
}
urls = {
    "okex": "https://www.okex.com/spot/trade#product={}",
    "binance": "https://www.binance.com/en/trade/{}"
}

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    os._exit(1)

to_write = queue.Queue()
i = 1


def writer():
    global i
    for text in iter(to_write.get, None):
        screen = driver.get_screenshot_as_png()
        img = draw_on_screen(screen, text)
        img.save("./screens/feed_{}_{}.png".format(args.feed, i))


def on_value(value):
    print(colored("{} price: {}".format(args.feed, value['price']), "cyan"))
    to_write.put("!!!!!!!!!!!!!!!!!!!!!!!!!!!!! {} price: {}".format(args.feed, value['price']))


feed = feeds[args.feed]()
feed.subscribe(on_value)
feed.feed(args.pair)

driver = create_driver()
driver.get(urls[args.feed].format(args.pair.replace("-", "_")))

t = threading.Thread(target=writer)
t.daemon = True
t.start()

try:
    while True:
        time.sleep(0.1)
except Exception:
    to_write.put(None)
    os._exit(1)
