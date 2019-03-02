from unittest import TestCase, main

from core import float_to_str
from feeds.feed import Feed
from pprint import pprint
from decimal import Decimal

depth_msg = {'asks': [['136.27000000', '17.00000000', []],
                      ['136.28000000', '0.08501000', []],
                      ['136.29000000', '8.10017000', []],
                      ['136.33000000', '7.33960000', []],
                      ['136.34000000', '0.11353000', []],
                      ['136.35000000', '0.68852000', []],
                      ['136.36000000', '0.11050000', []],
                      ['136.37000000', '23.34743000', []],
                      ['136.38000000', '0.10000000', []],
                      ['136.39000000', '85.45530000', []],
                      ['136.40000000', '150.47586000', []],
                      ['136.41000000', '673.00030000', []],
                      ['136.42000000', '0.31500000', []],
                      ['136.43000000', '1.00000000', []],
                      ['136.44000000', '0.50000000', []],
                      ['136.48000000', '35.95894000', []],
                      ['136.49000000', '10.82075000', []],
                      ['136.50000000', '815.21964000', []],
                      ['136.51000000', '1.12524000', []],
                      ['136.52000000', '37.91153000', []]],
             'bids': [['136.23000000', '1.23524000', []],
                      ['136.22000000', '0.00005000', []],
                      ['136.21000000', '11.86605000', []],
                      ['136.19000000', '4.00000000', []],
                      ['136.18000000', '11.68055000', []],
                      ['136.17000000', '0.73400000', []],
                      ['136.15000000', '4.00000000', []],
                      ['136.14000000', '2.87515000', []],
                      ['136.10000000', '31.50495000', []],
                      ['136.04000000', '0.70473000', []],
                      ['136.03000000', '1.98486000', []],
                      ['136.00000000', '2.32372000', []],
                      ['135.98000000', '0.73539000', []],
                      ['135.94000000', '4.02000000', []],
                      ['135.93000000', '18.88542000', []],
                      ['135.92000000', '4.23671000', []],
                      ['135.91000000', '27.17105000', []],
                      ['135.90000000', '26.47454000', []],
                      ['135.87000000', '1.16008000', []],
                      ['135.82000000', '51.32500000', []]],
             'lastUpdateId': 320672453}

depth_delta_full_msg = {'action': 'update',
                        'data': [{'asks': [['135.969', '0.01', 1],
                                           ['135.9718', '18.68', 1],
                                           ['135.972', '0.111977', 3],
                                           ['135.9749', '0', 0],
                                           ['135.975', '0', 0],
                                           ['136.0379', '3', 1],
                                           ['136.0502', '0.358', 1],
                                           ['136.0535', '0', 0],
                                           ['136.0541', '0.732', 1],
                                           ['136.0555', '0', 0],
                                           ['136.0612', '0', 0],
                                           ['136.2741', '0', 0],
                                           ['136.2823', '0', 0],
                                           ['136.3117', '12', 1],
                                           ['136.3151', '0', 0],
                                           ['142.51', '40', 1],
                                           ['142.55', '5.479276', 1]],
                                  'bids': [['135.931', '0.591649', 4],
                                           ['135.92', '12.45', 1],
                                           ['135.9199', '9.999999', 1],
                                           ['135.9198', '0', 0],
                                           ['135.9056', '5.98', 1],
                                           ['135.9027', '0', 0],
                                           ['135.9026', '0', 0],
                                           ['135.8896', '0', 0],
                                           ['135.8895', '0.214597', 1],
                                           ['135.8871', '0', 0],
                                           ['135.8841', '0.503004', 1],
                                           ['135.8641', '5.999999', 1],
                                           ['135.864', '0', 0],
                                           ['135.8614', '1.900663', 3],
                                           ['135.8499', '0.2845', 1],
                                           ['135.8483', '0', 0],
                                           ['135.8479', '3.041062', 3],
                                           ['135.8378', '0.010999', 1],
                                           ['135.8377', '0', 0],
                                           ['135.7785', '0', 0],
                                           ['135.7767', '0', 0],
                                           ['135.7612', '2.945479', 1],
                                           ['135.7155', '0', 0],
                                           ['135.6091', '0', 0],
                                           ['135.5884', '0', 0],
                                           ['135.5798', '7.355564', 1],
                                           ['135.5505', '44.133374', 2],
                                           ['128.889', '1', 1],
                                           ['128.8267', '0.141', 1],
                                           ['128.8', '5', 1],
                                           ['128.7897', '0.30568', 1],
                                           ['128.7657', '52.875', 1]],
                                  'checksum': -1081826157,
                                  'instrument_id': 'ETH-USDT',
                                  'timestamp': '2019-03-01T10:33:30.234Z'}],
                        'table': 'spot/depth'}

depth_delta_msg = {'asks': [['135.969', '0.01', 1],
                            ['135.9718', '18.68', 1],
                            ['135.972', '0.111977', 3],
                            ['135.9749', '0', 0],
                            ['135.975', '0', 0],
                            ['136.0379', '3', 1],
                            ['136.0502', '0.358', 1],
                            ['136.0535', '0', 0],
                            ['136.0541', '0.732', 1],
                            ['136.0555', '0', 0],
                            ['136.0612', '0', 0],
                            ['136.2741', '0', 0],
                            ['136.2823', '0', 0],
                            ['136.3117', '12', 1],
                            ['136.3151', '0', 0],
                            ['142.51', '40', 1],
                            ['142.55', '5.479276', 1]],
                   'bids': [['135.931', '0.591649', 4],
                            ['135.92', '12.45', 1],
                            ['135.9199', '9.999999', 1],
                            ['135.9198', '0', 0],
                            ['135.9056', '5.98', 1],
                            ['135.9027', '0', 0],
                            ['135.9026', '0', 0],
                            ['135.8896', '0', 0],
                            ['135.8895', '0.214597', 1],
                            ['135.8871', '0', 0],
                            ['135.8841', '0.503004', 1],
                            ['135.8641', '5.999999', 1],
                            ['135.864', '0', 0],
                            ['135.8614', '1.900663', 3],
                            ['135.8499', '0.2845', 1],
                            ['135.8483', '0', 0],
                            ['135.8479', '3.041062', 3],
                            ['135.8378', '0.010999', 1],
                            ['135.8377', '0', 0],
                            ['135.7785', '0', 0],
                            ['135.7767', '0', 0],
                            ['135.7612', '2.945479', 1],
                            ['135.7155', '0', 0],
                            ['135.6091', '0', 0],
                            ['135.5884', '0', 0],
                            ['135.5798', '7.355564', 1],
                            ['135.5505', '44.133374', 2],
                            ['128.889', '1', 1],
                            ['128.8267', '0.141', 1],
                            ['128.8', '5', 1],
                            ['128.7897', '0.30568', 1],
                            ['128.7657', '52.875', 1]],
                   'checksum': -1081826157,
                   'instrument_id': 'ETH-USDT',
                   'timestamp': '2019-03-01T10:33:30.234Z'
                   }


def create_feed():
    feed = Feed()
    feed.min_qty = 1.0
    return feed


class FeedTest(TestCase):
    def test_subscribe_unsubscribe(self):
        feed = create_feed()
        on_value = lambda: False
        feed.subscribe(on_value)
        feed.unsubscribe(on_value)

    def test_bids_from_msg(self):
        feed = create_feed()
        self.assertRaises(
            Exception,
            feed.bids_from_msg
        )

    def test_asks_from_msg(self):
        feed = create_feed()
        self.assertRaises(
            Exception,
            feed.asks_from_msg
        )

    def test_process_full_depth_message(self):
        feed = create_feed()
        feed.ask_bid_deleted = lambda ask_bid: float(ask_bid[0]) == 0
        feed.bids_from_msg = lambda msg: msg['bids']
        feed.asks_from_msg = lambda msg: msg['asks']

        expected_msg = {
            "price": {
                "sell": '136.23000000',
                "buy": '136.27000000'
            }
        }
        on_value = lambda msg: self.assertEqual(msg, expected_msg)
        feed.subscribe(on_value)
        feed.process_full_depth_message(depth_msg)

        self.assertEqual(
            feed.bids,
            depth_msg['bids']
        )
        self.assertEqual(
            feed.asks,
            depth_msg['asks']
        )
        self.assertEqual(
            feed.process_depth_message,
            feed.process_full_depth_message
        )

        feed.depth_update_with_delta = True

        feed.process_full_depth_message(depth_msg)
        self.assertEqual(
            feed.process_depth_message,
            feed.process_delta_depth_message
        )

    def test_process_depth_delta_message(self):
        feed = create_feed()
        feed.ask_bid_deleted = lambda ask_bid: int(ask_bid[2]) == 0
        feed.bids_from_msg = lambda msg: msg["data"][0]['bids']
        feed.asks_from_msg = lambda msg: msg["data"][0]['asks']
        feed.best_ask = feed.buy_empty
        feed.best_bid = feed.sell_empty
        feed.bids = [
            ['135.9027', '0', 0],
            ['135.9026', '0', 0],
            ['135.8896', '0', 0],
            ['136.21000000', '11.86605000', 2],
            ['136.19000000', '4.00000000', 1],
            ['136.18000000', '11.68055000', 3],
            ['136.17000000', '0.73400000', 4],
        ]
        feed.asks = [
            ['136.0555', '0', 0],
            ['136.0612', '0', 0],
            ['136.2741', '0', 0],
            ['136.2823', '0', 0],
            ['136.28000000', '0.08501000', 1],
            ['136.29000000', '8.10017000', 2],
            ['136.33000000', '7.33960000', 3],
        ]

        expected_msg = {
            "price": {
                "sell": '135.92',
                "buy": '135.9718'
            }
        }
        on_value = lambda msg: self.assertEqual(msg, expected_msg)
        feed.subscribe(on_value)

        feed.process_delta_depth_message(depth_delta_full_msg)

        self.assertEqual(
            feed.bids,
            [
                ['136.21000000', '11.86605000', 2],
                ['136.19000000', '4.00000000', 1],
                ['136.18000000', '11.68055000', 3],
                ['136.17000000', '0.73400000', 4],
                # above bids remain, below ones added
                ['135.931', '0.591649', 4],
                ['135.92', '12.45', 1],
                ['135.9199', '9.999999', 1],
                ['135.9056', '5.98', 1],
                ['135.8895', '0.214597', 1],
                ['135.8841', '0.503004', 1],
                ['135.8641', '5.999999', 1],
                ['135.8614', '1.900663', 3],
                ['135.8499', '0.2845', 1],
                ['135.8479', '3.041062', 3],
                ['135.8378', '0.010999', 1],
                ['135.7612', '2.945479', 1],
                ['135.5798', '7.355564', 1],
                ['135.5505', '44.133374', 2],
                ['128.889', '1', 1],
                ['128.8267', '0.141', 1],
                ['128.8', '5', 1],
                ['128.7897', '0.30568', 1],
                ['128.7657', '52.875', 1]
            ]
        )
        self.assertEqual(
            feed.asks,
            [
                ['136.28000000', '0.08501000', 1],
                ['136.29000000', '8.10017000', 2],
                ['136.33000000', '7.33960000', 3],
                # above asks remain, below ones added
                ['135.969', '0.01', 1],
                ['135.9718', '18.68', 1],
                ['135.972', '0.111977', 3],
                ['136.0379', '3', 1],
                ['136.0502', '0.358', 1],
                ['136.0541', '0.732', 1],
                ['136.3117', '12', 1],
                ['142.51', '40', 1],
                ['142.55', '5.479276', 1]
            ]
        )

    def test_emit_from_full_depth(self):
        feed = create_feed()

        bids = depth_msg['bids']
        asks = depth_msg['asks']
        expected_msg = {
            "price": {
                "sell": '136.23000000',
                "buy": '136.27000000'
            }
        }
        on_value = lambda msg: self.assertEqual(msg, expected_msg)
        feed.subscribe(on_value)
        feed.emit_from_full_depth(bids, asks)

        self.assertEqual(
            feed.best_bid,
            Decimal('136.23')
        )
        self.assertEqual(
            feed.best_ask,
            Decimal('136.27')
        )

    def test_emit_from_delta(self):
        feed = create_feed()

        expecting_msg = {
            "price": {
                "sell": '135.92',
                "buy": '135.9718'
            }
        }
        on_emit = lambda msg: self.assertEqual(msg, expecting_msg)
        feed.subscribe(on_emit)

        feed.asks = depth_delta_msg['asks']
        feed.bids = depth_delta_msg['bids']
        feed.best_bid = feed.sell_empty
        feed.best_ask = feed.buy_empty

        feed.emit_from_delta()

    def test_emit_from_depth(self):
        feed = create_feed()

        best_bid = Decimal('136.23000000')
        best_ask = Decimal('136.27000000')
        expecting_msg = {
            "price": {
                "sell": float_to_str(best_bid),
                "buy": float_to_str(best_ask),
            }
        }
        on_emit = lambda msg: self.assertEqual(msg, expecting_msg)
        feed.best_bid = best_bid
        feed.best_ask = best_ask
        feed.subscribe(on_emit)

        feed.emit_from_depth()

        feed.best_ask = feed.buy_empty
        feed.emit_from_depth()

        feed.best_bid = feed.sell_empty
        feed.emit_from_depth()

    def test_reduce_depth(self):
        feed = create_feed()

        self.assertEqual(
            feed.reduce_depth(
                [feed.sell_empty] + depth_msg['bids'],
                None
            ),
            Decimal('136.23000000')
        )
        self.assertEqual(
            feed.reduce_depth(
                None,
                [feed.buy_empty] + depth_msg['asks'],
            ),
            Decimal('136.27000000')
        )

    def test_compare_bid(self):
        feed = create_feed()

        self.assertEqual(
            # price is ok but volume is not enough
            feed.compare_bid(
                '136.21000000',
                ['136.27000000', '0.73400000', []]
            ),
            '136.21000000'
        )
        self.assertEqual(
            # volume is ok but price is lower
            feed.compare_bid(
                '136.21000000',
                ['135.27000000', '1.73400000', []]
            ),
            '136.21000000'
        )
        self.assertEqual(
            # price is higher and volume is ok
            feed.compare_bid(
                '136.21000000',
                ['137.27000000', '1.73400000', []]
            ),
            Decimal('137.27000000')
        )

    def test_compare_ask(self):
        feed = create_feed()

        self.assertEqual(
            # price is ok but volume is not enough
            feed.compare_ask(
                '135.82000000',
                ['134.17000000', '0.73400000', []],
            ),
            '135.82000000'
        )
        self.assertEqual(
            # volume is enough but price is higher
            feed.compare_ask(
                '135.82000000',
                ['136.17000000', '1.73400000', []],
            ),
            '135.82000000'
        )
        self.assertEqual(
            # volume is enough and price is lower
            feed.compare_ask(
                '135.82000000',
                ['134.17000000', '1.73400000', []],
            ),
            Decimal('134.17000000')
        )

    def test_filter_ask_bid(self):
        feed = create_feed()
        feed.ask_bid_deleted = lambda ask_bid: int(ask_bid[2]) == 0

        self.assertEqual(
            feed.filter_empty_ask_bids(
                [['135.931', '0.591649', 4],
                 ['135.92', '12.45', 1],
                 ['135.9199', '9.999999', 1],
                 ['135.9198', '0', 0],
                 ['135.9056', '5.98', 1],
                 ['135.9027', '0', 0],
                 ['135.9026', '0', 0],
                 ['135.8896', '0', 0],
                 ['135.8895', '0.214597', 1],
                 ['135.8871', '0', 0],
                 ['135.8841', '0.503004', 1],
                 ['135.8641', '5.999999', 1],
                 ['135.864', '0', 0],
                 ['135.8614', '1.900663', 3],
                 ['135.8499', '0.2845', 1],
                 ['135.8483', '0', 0],
                 ['135.8479', '3.041062', 3],
                 ['135.8378', '0.010999', 1],
                 ['135.8377', '0', 0],
                 ['135.7785', '0', 0],
                 ['135.7767', '0', 0],
                 ['135.7612', '2.945479', 1],
                 ['135.7155', '0', 0],
                 ['135.6091', '0', 0],
                 ['135.5884', '0', 0],
                 ['135.5798', '7.355564', 1],
                 ['135.5505', '44.133374', 2],
                 ['128.889', '1', 1],
                 ['128.8267', '0.141', 1],
                 ['128.8', '5', 1],
                 ['128.7897', '0.30568', 1],
                 ['128.7657', '52.875', 1]]
            ),
            [['135.931', '0.591649', 4],
             ['135.92', '12.45', 1],
             ['135.9199', '9.999999', 1],
             ['135.9056', '5.98', 1],
             ['135.8895', '0.214597', 1],
             ['135.8841', '0.503004', 1],
             ['135.8641', '5.999999', 1],
             ['135.8614', '1.900663', 3],
             ['135.8499', '0.2845', 1],
             ['135.8479', '3.041062', 3],
             ['135.8378', '0.010999', 1],
             ['135.7612', '2.945479', 1],
             ['135.5798', '7.355564', 1],
             ['135.5505', '44.133374', 2],
             ['128.889', '1', 1],
             ['128.8267', '0.141', 1],
             ['128.8', '5', 1],
             ['128.7897', '0.30568', 1],
             ['128.7657', '52.875', 1]]
        )

    def test_ask_bid_deleted(self):
        feed = create_feed()

        self.assertRaises(
            Exception,
            feed.ask_bid_deleted,
            depth_msg['bids'][0]
        )

    def test_ask_bid_volume(self):
        feed = create_feed()

        self.assertEqual(
            feed.ask_bid_volume(
                depth_msg['bids'][0]
            ),
            Decimal('1.23524000')
        )
        self.assertEqual(
            feed.ask_bid_volume(
                depth_msg['asks'][0]
            ),
            Decimal('17.00000000')
        )

    def test_check_volume(self):
        feed = create_feed()

        bid_enough = depth_msg['bids'][0]
        bid_less = depth_msg['bids'][1]
        ask_enough = depth_msg['asks'][0]
        ask_less = depth_msg['asks'][1]

        self.assertEqual(
            feed.check_volume(
                bid_enough
            ),
            True
        )
        self.assertEqual(
            feed.check_volume(
                bid_less
            ),
            False
        )

        self.assertEqual(
            feed.check_volume(
                ask_enough
            ),
            True
        )
        self.assertEqual(
            feed.check_volume(
                ask_less
            ),
            False
        )

    def test_ask_bid_price(self):
        feed = create_feed()
        self.assertEqual(
            feed.ask_bid_price(
                depth_msg['asks'][0],
            ),
            Decimal('136.27000000')
        )

        self.assertEqual(
            feed.ask_bid_price(
                depth_msg['bids'][0],
            ),
            Decimal('136.23000000')
        )


if __name__ == '__main__':
    main()
