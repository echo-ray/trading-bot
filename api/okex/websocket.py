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
from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.error import ReactorAlreadyRunning
from pprint import pprint
import os


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


class OkexReconnectingClientFactory(ReconnectingClientFactory):

    # set initial delay to a short time
    initialDelay = 0.1

    maxDelay = 10

    maxRetries = 5


class OkexClientProtocol(WebSocketClientProtocol):
    def onOpen(self):
        if self.factory.subscribe_msg:
            self.sendMessage(self.factory.subscribe_msg)

    def onConnect(self, response):
        # reset the delay after reconnecting
        self.factory.resetDelay()

    def onMessage(self, payload, isBinary):
        payload_obj = json.loads(inflate(payload).decode('utf8'))
        self.factory.callback(payload_obj)


class OkexClientFactory(WebSocketClientFactory, OkexReconnectingClientFactory):
    protocol = OkexClientProtocol
    _reconnect_error_payload = {
        'e': 'error',
        'm': 'Max reconnect retries reached'
    }

    def clientConnectionFailed(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.callback(self._reconnect_error_payload)

    def clientConnectionLost(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.callback(self._reconnect_error_payload)


class OkexWebsocketManager(Thread):
    def __init__(self):
        super().__init__()
        self._conns = {}

    def run(self):
        try:
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            # Ignore error about reactor already running
            pass

    def _start_socket(self, path, callback, subscribe_msg, socket_url):
        factory_url = socket_url
        factory = OkexClientFactory(factory_url)
        factory.protocol = OkexClientProtocol
        factory.callback = callback
        factory.reconnect = True
        context_factory = ssl.ClientContextFactory()
        factory.subscribe_msg = subscribe_msg

        self._conns[path] = connectWS(factory, context_factory)
        return self._conns[path]

    def start_depth_socket(self, pair, cb, socket_url="wss://okexcomreal.bafang.com:10441/websocket"):
        path = "@depth/{}".format(pair)
        base, quote = pair.lower().split("-")
        add_channel_msg = json.dumps({
            "event": "addChannel",
            "parameters": {
                "base": base,
                "binary": "0",
                "product": "spot",
                "quote": quote,
                "type": "depth",
            }
        })
        subscribe_msg = add_channel_msg.encode("utf8")
        self._start_socket(path, cb, subscribe_msg, socket_url)

    def stop_socket(self, conn_key):
        """Stop a websocket given the connection key

        :param conn_key: Socket connection key
        :type conn_key: string

        :returns: connection key string if successful, False otherwise
        """
        if conn_key not in self._conns:
            return

        # disable reconnecting if we are closing
        self._conns[conn_key].factory = WebSocketClientFactory(self.STREAM_URL + 'tmp_path')
        self._conns[conn_key].disconnect()
        del(self._conns[conn_key])

        # check if we have a user stream socket
        if len(conn_key) >= 60 and conn_key[:60] == self._user_listen_key:
            self._stop_user_socket()

    def _stop_user_socket(self):
        if not self._user_listen_key:
            return
        # stop the timer
        self._user_timer.cancel()
        self._user_timer = None
        self._user_listen_key = None

    def close(self):
        """Close all connections

        """
        keys = set(self._conns.keys())
        for key in keys:
            self.stop_socket(key)

        self._conns = {}


class OkexWebSocket(metaclass=Singleton):
    def __init__(self, pair):
        self.order_update_table = "spot/order"
        channels = [
            self.order_update_table + ":" + pair,
        ]

        sm = OkexWebsocketManager()
        sm.daemon = True
        sm.start_depth_socket(pair, self.process_depth_message)
        sm.start()

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

    def process_depth_message(self, payload):
        msg = payload[0]
        if 'channel' not in msg:
            if msg['product'] == "spot" and msg['type'] == "depth":
                self.on_feed(msg)

