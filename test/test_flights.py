import unittest
import os
from datetime import time

from ooc import Flights, ft


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.
    :param rel_path: PAth relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


class TestFlights(unittest.TestCase):
    """
    This test case is used to test :class:`ooc.Flights`.
    """

    def test_load_flight_data(self):
        flights = Flights(abs_path("flight_data"))
        assert flights.flight_data[0].flight_type == ft.Full
        assert flights.flight_data[0][0] == ft.Full
        assert flights.flight_data[0].eta == time(20, 30)
        assert flights.flight_data[56].flight_type == ft.Dep
        assert flights.flight_data[26].ac_type == "E90"


if __name__ == '__main__':
    unittest.main()
