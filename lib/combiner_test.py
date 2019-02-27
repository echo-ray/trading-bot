from lib.combiner import Combiner
from unittest import TestCase, main


class CombinerTest(TestCase):
    def test_emit(self):
        expected = (1, 2)
        on_value = lambda v: self.assertEqual(v, expected)
        combiner = Combiner(on_value, False)
        combiner.on_left(1)
        combiner.on_right(2)

        expected = (1, 3)
        combiner.on_right(3)

        expected = (2, 3)
        combiner.on_left(2)


if __name__ == '__main__':
    main()
