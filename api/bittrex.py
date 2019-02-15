def normalize_pair(pair):
    asset, quote = pair.split("-")
    return "{}-{}".format(quote, asset)


DELTA_TYPE_ADD = 0
DELTA_TYPE_REMOVE = 1
DELTA_TYPE_UPDATE = 2

