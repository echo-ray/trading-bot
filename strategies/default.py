import sys
from termcolor import colored
from core import split_pair, round_down
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-d", "--diff", dest="diff",
                    help="diff between prices to execute step", default="0.03")

args, extra = parser.parse_known_args()

transitions = {
  "1": "1.5",
  "1.5": "2",
  "2": "2.5",
  "2.5": "1"
}

diff = float(args.diff)


def perform_step(binance_price, okex_price, binance_client, okex_client, pair, step):
    try:
        if step == "1":
            return perform_step_one(binance_price, okex_price, binance_client, okex_client, pair)
        if step == "2":
            return perform_step_two(binance_price, okex_price, binance_client, okex_client, pair)
        if step == "1.5" or step == "2.5":
            print(colored("waiting for okex order execution", "cyan"))
            return False
    except Exception as e:
        print("error during perform step", step, ":", e)
        sys.exit(1)

    return False


def perform_step_one(binance_price, okex_price, binance_client, okex_client, pair):
    if (float(okex_price) - float(binance_price)) >= diff:
        print_balance(binance_client, okex_client, "1")

        binance_success = buy_asset(binance_price, binance_client, pair)
        okex_success = sell_asset(okex_price, okex_client, pair)

        assert_success(binance_success, okex_success)

        return binance_success and okex_success

    return False


def perform_step_two(binance_price, okex_price, binance_client, okex_client, pair):
    if (float(binance_price) - float(okex_price)) >= diff:
        print_balance(binance_client, okex_client, "2")

        binance_success = sell_asset(binance_price, binance_client, pair)
        okex_success = buy_asset(okex_price, okex_client, pair)

        assert_success(binance_success, okex_success)

        return binance_success and okex_success

    return False


def assert_success(binance_success, okex_success):
    if binance_success:
        if not okex_success:
            raise Exception("binance order succedeed while okex doesn't")

    if okex_success:
        if not binance_success:
            raise Exception("okex order succedeed while binance doesn't")


def print_balance(client_one, client_two, step):
    print(colored("step {}:".format(step), "yellow"))
    print(colored("{} balance {}".format(client_one.exchange, client_one.balance), 'yellow'))
    print(colored("{} balance {}".format(client_two.exchange, client_two.balance), 'yellow'))


def buy_asset(price, client, pair):
    asset, quote = split_pair(pair)
    balance_quote = float(client.get_balance(quote))
    buy_count = round_down(
        balance_quote / float(price),
        2
    )

    print(colored("buying {} of {} on {}".format(buy_count, asset, client.exchange), "green"))

    return client.buy(
        price,
        str(buy_count),
        pair
    )


def sell_asset(price, client, pair):
    asset, quote = split_pair(pair)
    asset_quote = float(client.get_balance(asset))
    sell_count = round_down(
        asset_quote / 2,
        2
    )
    print(colored("selling {} of {} on {}".format(sell_count, asset, client.exchange), "red"))

    return client.sell(
        price,
        str(sell_count),
        pair
    )
