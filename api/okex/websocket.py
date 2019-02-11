import asyncio
import websockets
import json
import requests
import dateutil.parser as dp
import hmac
import base64
import zlib
import hashlib
from threading import Thread
from lib.singleton import Singleton
import api.okex.credentials as creds


def get_server_time():
    url = "http://www.okex.com/api/general/v3/time"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['iso']
    else:
        return ""


def server_timestamp():
    server_time = get_server_time()
    parsed_t = dp.parse(server_time)
    timestamp = parsed_t.timestamp()
    return timestamp


def login_params(timestamp, api_key, passphrase, secret_key):
    message = timestamp + 'GET' + '/users/self/verify'
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod=hashlib.sha256)
    d = mac.digest()
    sign = base64.b64encode(d)

    login_param = {"op": "login", "args": [api_key, passphrase, timestamp, sign.decode("utf-8")]}
    login_str = json.dumps(login_param)
    return login_str


def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


# subscribe channel without login
#
# swap/ticker // 行情数据频道
# swap/candle60s // 1分钟k线数据频道
# swap/candle180s // 3分钟k线数据频道
# swap/candle300s // 5分钟k线数据频道
# swap/candle900s // 15分钟k线数据频道
# swap/candle1800s // 30分钟k线数据频道
# swap/candle3600s // 1小时k线数据频道
# swap/candle7200s // 2小时k线数据频道
# swap/candle14400s // 4小时k线数据频道
# swap/candle21600 // 6小时k线数据频道
# swap/candle43200s // 12小时k线数据频道
# swap/candle86400s // 1day k线数据频道
# swap/candle604800s // 1week k线数据频道
# swap/trade // 交易信息频道
# swap/funding_rate//资金费率频道
# swap/price_range//限价范围频道
# swap/depth //深度数据频道，首次200档，后续增量
# swap/depth5 //深度数据频道，每次返回前5档
# swap/mark_price// 标记价格频道
async def _subscribe_without_login(url, channels):
    async with websockets.connect(url) as websocket:
        sub_param = {"op": "subscribe", "args": channels}
        sub_str = json.dumps(sub_param)
        await  websocket.send(sub_str)
        print(f"send: {sub_str}")

        print("receive:")
        res = await websocket.recv()
        res = inflate(res)
        print(f"{res}")

        res = await websocket.recv()
        res = inflate(res)
        print(f"{res}")


# subscribe channel need login
#
# swap/account //用户账户信息频道
# swap/position //用户持仓信息频道
# swap/order //用户交易数据频道
async def _subscribe(url, api_key, passphrase, secret_key, channels, cb):
    async with websockets.connect(url) as websocket:
        # login
        timestamp = server_timestamp()
        login_str = login_params(str(timestamp), api_key, passphrase, secret_key)

        await websocket.send(login_str)

        login_res = await websocket.recv()

        sub_param = {"op": "subscribe", "args": channels}
        sub_str = json.dumps(sub_param)

        await websocket.send(sub_str)

        res = await websocket.recv()
        res = inflate(res)

        while True:
            res = await websocket.recv()
            res = inflate(res)
            cb(
                json.loads(res.decode("utf-8"))
            )


# unsubscribe channels
async def _unsubscribe(url, api_key, passphrase, secret_key, channels):
    async with websockets.connect(url) as websocket:
        timestamp = str(server_timestamp())

        login_str = login_params(str(timestamp), api_key, passphrase, secret_key)

        await websocket.send(login_str)

        greeting = await websocket.recv()
        # print(f"receive < {greeting}")

        sub_param = {"op": "unsubscribe", "args": channels}
        sub_str = json.dumps(sub_param)
        await websocket.send(sub_str)
        print(f"send: {sub_str}")

        res = await websocket.recv()
        res = inflate(res)
        print(f"{res}")


# unsubscribe channels
async def _unsubscribe_without_login(url, channels):
    async with websockets.connect(url) as websocket:
        sub_param = {"op": "unsubscribe", "args": channels}
        sub_str = json.dumps(sub_param)
        await  websocket.send(sub_str)
        print(f"send: {sub_str}")

        res = await websocket.recv()
        res = inflate(res)
        print(f"{res}")


url = 'wss://real.okex.com:10442/ws/v3'


def subscribe(api_key, passphrase, secret_key, channels, cb):
    loop = asyncio.new_event_loop()
    t = Thread(
        target=lambda loop: loop.run_until_complete(_subscribe(url, api_key, passphrase, secret_key, channels, cb)),
        args=(loop,)
    )
    t.daemon = True
    t.start()
    return t


async def _subscribe_to_prod(channels, cb):
    async with websockets.connect("wss://okexcomreal.bafang.com:10441/websocket") as websocket:
        for channel in channels:
            message = json.dumps({
                "event": "addChannel",
                "parameters": {
                    "binary": "0",
                    **channel
                }
            })
            await websocket.send(message)

        await websocket.recv()

        while True:
            res = await websocket.recv()
            res = inflate(res)
            cb(
                json.loads(res.decode("utf-8"))
            )


def subscribe_to_prod(channels, cb):
    loop = asyncio.new_event_loop()
    t = Thread(
        target=lambda loop: loop.run_until_complete(_subscribe_to_prod(channels, cb)),
        args=(loop,)
    )
    t.daemon = True
    t.start()
    return t


class OkexWebSocket(metaclass=Singleton):
    def __init__(self, pair):
        self.feed_table = "all_ticker_3s"
        self.order_update_table = "spot/order"
        channels = [
            self.order_update_table + ":" + pair
        ]
        prod_channels = [
            {
                "base": "eth",
                "product": "spot",
                "quote": "usdt",
                "type": "ticker",
            }
        ]
        subscribe_to_prod(
            prod_channels,
            self.process_prod_message,
        )
        subscribe(
            creds.api_key,
            creds.pass_phrase,
            creds.secret_key,
            channels,
            self.process_message
        )
        self.on_feed = lambda msg: False
        self.on_order_update = lambda msg: False

    def subscribe_to_order_update(self, cb):
        self.on_order_update = cb

    def subscribe_to_feed(self, cb):
        self.on_feed = cb

    def process_message(self, msg):
        if 'table' in msg:
            if msg['table'] == self.order_update_table:
                self.on_order_update(msg)

    def process_prod_message(self, msg):
        self.on_feed(msg)

