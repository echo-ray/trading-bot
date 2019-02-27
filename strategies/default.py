from termcolor import colored
from core import split_pair, round_down, float_to_str, calculate_buy_count
import os
from lib.config import Config

args = Config.get_args()

transitions = {
    "1": "1.3",
    "1.3": "1.6",
    "1.6": "2",
    "2": "2.3",
    "2.3": "2.6",
    "2.6": "1"
}

leftExc, rightExc = args.exchanges

trade_quantity = float(args.quantity)
buy_side = args.buy_side if args.buy_side else leftExc
sell_side = args.sell_side if args.sell_side else rightExc

lock = False


def calculate_diff(left_price, right_price):
    if args.diff:
        return float(args.diff)

    return (((float(left_price) + float(right_price)) / 2) * 0.0025) * 1.5


def perform_step(left_price, right_price, left_client, right_client, pair, step):
    global lock

    if lock:
        return False

    try:
        if step == "1":
            return perform_step_one(left_price, right_price, left_client, right_client, pair)
        if step == "2":
            return perform_step_two(left_price, right_price, left_client, right_client, pair)
        if step.find(".") > -1:
            print(colored("waiting for order(s) execution", "cyan"))
            return False
    except Exception as e:
        print("error during perform step", step, ":", e)
        os._exit(1)

    return False


def perform_step_one(left_price, right_price, left_client, right_client, pair):
    global buy_side
    global sell_side
    global lock

    right_sell_diff = calculate_diff(left_price["buy"], right_price["sell"])
    if (float(right_price["sell"]) - float(left_price["buy"])) >= right_sell_diff:

        lock = True

        print_balance(left_client, right_client, "1")

        left_side_success = buy_asset(left_price["buy"], left_client, pair)
        right_side_success = sell_asset(right_price["sell"], right_client, pair)

        assert_success(left_side_success, right_side_success)

        buy_side = leftExc
        sell_side = rightExc

        lock = False

        return left_side_success and right_side_success

    left_sell_diff = calculate_diff(left_price["sell"], right_price["buy"])
    if (float(left_price["sell"]) - float(right_price["buy"])) >= left_sell_diff:

        lock = True

        print_balance(left_client, right_client, "1")

        left_side_success = sell_asset(left_price["sell"], left_client, pair)
        right_side_success = buy_asset(right_price["buy"], right_client, pair)

        assert_success(left_side_success, right_side_success)

        buy_side = rightExc
        sell_side = leftExc

        lock = False

        return left_side_success and right_side_success

    return False


def perform_step_two(left_price, right_price, left_client, right_client, pair):
    global lock

    if buy_side == leftExc:
        left_sell_diff = calculate_diff(left_price["sell"], right_price["buy"])
        if (float(left_price["sell"]) - float(right_price["buy"])) >= left_sell_diff:

            lock = True

            print_balance(left_client, right_client, "2")

            left_side_success = sell_asset(left_price["sell"], left_client, pair)
            right_side_success = buy_asset(right_price["buy"], right_client, pair)

            assert_success(left_side_success, right_side_success)

            lock = False

            return left_side_success and right_side_success

    if buy_side == rightExc:
        right_sell_diff = calculate_diff(left_price["buy"], right_price["sell"])
        if (float(right_price["sell"]) - float(left_price["buy"])) >= right_sell_diff:

            lock = True

            print_balance(left_client, right_client, "2")

            left_side_success = buy_asset(left_price["buy"], left_client, pair)
            right_side_success = sell_asset(right_price["sell"], right_client, pair)

            assert_success(left_side_success, right_side_success)

            lock = False

            return left_side_success and right_side_success

    return False


def assert_success(left_side_success, right_side_success):
    if left_side_success:
        if not right_side_success:
            raise Exception("{} order succedeed while {} doesn't".format(leftExc, rightExc))

    if right_side_success:
        if not left_side_success:
            raise Exception("{} order succedeed while {} doesn't".format(rightExc, leftExc))


def print_balance(client_one, client_two, step):
    print(colored("step {}:".format(step), "yellow"))
    print(colored("{} balance {}".format(client_one.exchange, client_one.balance), 'yellow'))
    print(colored("{} balance {}".format(client_two.exchange, client_two.balance), 'yellow'))


def buy_asset(price, client, pair):
    asset, quote = split_pair(pair)
    buy_count = round_down(
        trade_quantity,
        8
    )
    buy_count = calculate_buy_count(
        buy_count,
        client.get_fee(pair, True)
    )

    print(colored("buying {} of {} on {} for {}".format(buy_count, asset, client.exchange, price), "green"))

    return client.buy(
        price,
        float_to_str(buy_count),
        pair
    )


def sell_asset(price, client, pair):
    asset, quote = split_pair(pair)
    sell_count = round_down(
        trade_quantity,
        2
    )
    print(colored("selling {} of {} on {} for {}".format(sell_count, asset, client.exchange, price), "red"))

    return client.sell(
        price,
        float_to_str(round_down(sell_count, 8)),
        pair
    )
