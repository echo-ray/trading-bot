from math import floor
import decimal


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
            '' + asset: float_to_str(balance_asset + quantity),
            '' + quote: float_to_str(balance_quote - (quantity * price))
        }
    else:
        return {
            '' + asset: float_to_str(balance_asset - quantity),
            '' + quote: float_to_str(balance_quote + (quantity * price))
        }


def split_pair(pair):
    return pair.split("-")


def minus_fee(price, fee):
    price = float(price)
    fee = float(fee)

    if fee > 1:
        return price - fee

    return price - (price * fee)


# create a new context for this task
ctx = decimal.Context()

# 20 digits should be enough for everyone :D
ctx.prec = 20


def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')
