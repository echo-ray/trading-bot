from lib.config import Config
from binance.client import Client
from binance.websockets import BinanceSocketManager
import requests
import hmac
import time
from urllib.parse import urlencode
import hashlib
from binance.exceptions import BinanceAPIException

config = Config()
credentials = config.credentials("binance.json")

api_key = credentials['apiKey']
api_secret = credentials['secret']


def create_client():
    return Client(api_key, api_secret)


def create_ws():
    client = create_client()
    return BinanceSocketManager(client)


def normalize_pair(pair):
    return pair.replace('-', '')


def get_fees():
    request_url = 'https://api.binance.com/wapi/v3/tradeFee.html?'

    timestamp = int(time.time() * 1000)

    querystring = urlencode({'timestamp': timestamp})

    signature = hmac.new(api_secret.encode('utf-8'), querystring.encode('utf-8'), hashlib.sha256).hexdigest()

    request_url += querystring + '&signature=' + signature

    r = requests.get(request_url, headers={"X-MBX-APIKEY": api_key})
    json = r.json()
    if not json['success']:
        raise BinanceAPIException(json['msg'])

    return json["tradeFee"]
