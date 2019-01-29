from math import floor


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
            '' + asset: str(balance_asset + quantity),
            '' + quote: str(balance_quote - (quantity * price))
        }
    else:
        return {
            '' + asset: str(balance_asset - quantity),
            '' + quote: str(balance_quote + (quantity * price))
        }


def split_pair(pair):
    return pair.split("-")


def minus_fee(price, fee):
    price = float(price)
    fee = float(fee)

    if fee > 1:
        return price - fee

    return price - (price * fee)
