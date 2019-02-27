from unittest import TestCase, main
import core


class CoreTest(TestCase):
    def test_round_down(self):
        self.assertEqual(
            core.round_down(10.123081290381023809128301983018230918230981230),
            10.12308129
        )

    def test_calculate_remains(self):
        pair = "ETH-USDT"
        price = 122.234
        quantity = 1
        fee = 0.001
        balance = {
            "ETH": 1,
            "USDT": 123.0
        }
        self.assertEqual(
            core.calculate_remains(
                pair,
                False,
                price,
                quantity,
                fee,
                balance,
            ),
            {
                "ETH": "0.0",
                "USDT": "245.111766"
            }
        )

        self.assertEqual(
            core.calculate_remains(
                pair,
                True,
                price,
                quantity,
                fee,
                balance,
            ),
            {
                "ETH": "1.999",
                "USDT": "0.7660000000000053"
            }
        )

    def test_split_pair(self):
        self.assertEqual(
            core.split_pair("ETH-USDT"),
            ["ETH", "USDT"]
        )

    def test_plus_fee(self):
        self.assertEqual(
            core.plus_fee(100, 0.001),
            100.1
        )

    def test_minus_fee(self):
        self.assertEqual(
            core.minus_fee(100, 0.001),
            99.9
        )

    # TODO not all tests pass
    def test_float_to_str(self):
        self.assertEqual(
            core.float_to_str(0.000000054321654321),
            '0.000000054321654321'
        )

    def test_calculate_buy_count(self):
        self.assertEqual(
            core.calculate_buy_count(
                100,
                0.0001
            ),
            100.0100010001
        )


if __name__ == '__main__':
    main()
