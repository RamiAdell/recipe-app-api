from django.test import SimpleTestCase

from . import calc


class CalcTests(SimpleTestCase):
    """ Testing """

    def test_add_numbers(self):
        """ Adding numbers together"""

        res = calc.add(5, 6)
        self.assertEqual(res, 11)

    def test_substracting_numbers(self):
        """ Adding numbers together"""

        res = calc.subtract(10, 15)
        self.assertEqual(res, 5)
