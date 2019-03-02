from math import floor
import decimal
import os

Decimal = decimal.Decimal


def round_down(n, d=8):
    d = int('1' + ('0' * d))
    return floor(n * d) / d


def calculate_remains(pair, buy, price, quantity, fee, balance):
    asset, quote = split_pair(pair)

    quantity = float(quantity)
    price = float(price)
    balance_asset = float(balance[asset])
    balance_quote = float(balance[quote])

    if buy:
        return {
            '' + asset: float_to_str(balance_asset + minus_fee(quantity, fee)),
            '' + quote: float_to_str(balance_quote - (quantity * price))
        }
    else:
        return {
            '' + asset: float_to_str(balance_asset - quantity),
            '' + quote: float_to_str(balance_quote + minus_fee((quantity * price), fee))
        }


def split_pair(pair):
    return pair.split("-")


def plus_fee(price, fee):
    price = float(price)
    fee = float(fee)

    return price + (price * fee)


def minus_fee(price, fee):
    price = float(price)
    fee = float(fee)
    return price - (price * fee)


def float_to_str(f):
    # create a new context for this task
    ctx = decimal.Context()

    # 20 digits should be enough for everyone :D
    ctx.prec = 40

    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    try:
        d1 = f if isinstance(f, Decimal) else ctx.create_decimal(repr(f))
        return format(d1, 'f')

    except Exception:
        print("failed to convert {} to string".format(f))
        os._exit(1)


count_precision = 2


def calculate_buy_count(count, fee, step_size):
    if Decimal(step_size) < 1:
        divider = 1 - Decimal(fee)
        return round_down(Decimal(count) / divider, count_precision)

    return round_down(count, count_precision)


def calculate_sell_count(count, step_size):
    return round_down(count, count_precision)
