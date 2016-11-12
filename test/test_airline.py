import unittest
import os

from ooc import Airport


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.
    :param rel_path: PAth relative to this file
    :return: Absolute path
    """

    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


class TestAirport(unittest.TestCase):
    """
    This is the test case for :class:`ooc.Airport`.
    """

    def test_load_airlines(self):
        airport = Airport(airlines_path=abs_path("./data/airlines.csv"))
        assert airport.airlines["KQ"] == (0, 0)
        assert airport.airlines["G9"] == (1, 1)
        assert airport.airlines["EY"] == (1, 1)
        assert airport.airlines["SA"] == (2, 2)

        print(airport.airlines)

    def test_load_terminal_bay_distance(self):
        pass
