import unittest
import os
from datetime import time

from ooc import Flights, Airport, ft


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
        """
        Checks whether the flight schedule data is loaded in properly. It
        Tests a few random data point in the table to see if those where loaded in correctly.
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.flight_schedule[0].flight_type, ft.Full)
        self.assertEquals(flights.flight_schedule[0][0], ft.Full)
        self.assertEquals(flights.flight_schedule[0].eta, time(20, 30))
        self.assertEquals(flights.flight_schedule[56].flight_type, ft.Dep)
        self.assertEquals(flights.flight_schedule[26].ac_type, "E90")
        self.assertIsNone(flights.flight_schedule[4].in_flight_no)
        self.assertEquals(flights.flight_schedule[0].in_flight_no, "BA065")
        self.assertEquals(flights.flight_schedule[15].in_flight_no, "KL565")

    def test_n_flights(self):
        """
        Check if the number of flights loaded in is correct.

        :return:
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.n_flights, 69)

    def test_n_passengers(self):
        """
        Checks whether the number of passengers for each flight is correct.

        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.n_passengers(0), 300)
        self.assertEquals(flights.n_passengers(40), 90)
        self.assertEquals(flights.n_passengers(60), 90)

    def test_airline(self):
        """
        Checks whether the airline detection code is working.

        :return:
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.airline(0), "BA")
        self.assertEquals(flights.airline(5), "ET")

    def test_terminal(self):
        """
        Checks whether the correct terminal has been found for the flights.
        :return:
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.terminal(0), "A")
        self.assertEquals(flights.terminal(5), "C")

    def test_preference(self):
        """
        Checks whether the preference table has been loaded in correctly.
        """
        # The preference function has to be implemented first.
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.preferences_table["KQ210"].dest, "BOM")
        self.assertEquals(flights.preferences_table["KQ210"].bays, (21,))
        self.assertEquals(flights.preferences_table["KQ210"].gates, (17,))
        self.assertEquals(flights.preferences_table["ET"].dest, "ADD")
        self.assertEquals(flights.preferences_table["ET"].bays, (11, 12))
        self.assertEquals(flights.preferences_table["ET"].gates, (7, 8))

        print(flights.flight_schedule[1])

    def test_load_adjacency(self):
        """
        Checks whether the adjacency matrix has been loaded correctly.
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)

        self.assertEquals(flights.adjacency[0], (8, 9))
        self.assertEquals(flights.adjacency[1], (13, 14))

    def test_domestic(self):
        """
        Checks whether domestic flights are detected correctly.

        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertIs(flights.domestic(0), False)
        self.assertIs(flights.domestic(48), True)

    def test_time_conflict(self):
        """
        Checks whether the time conflict function works correctly.

        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)

        self.assertIs(flights.time_conflict(4, 0), True)
        self.assertIs(flights.time_conflict(0, 4), True)
        self.assertIs(flights.time_conflict(0, 5), True)
        self.assertIs(flights.time_conflict(5, 0), True)
        self.assertIs(flights.time_conflict(6, 7), True)
        self.assertIs(flights.time_conflict(7, 6), True)

        self.assertIs(flights.time_conflict(1, 5), False)
        self.assertIs(flights.time_conflict(3, 5), False)
        self.assertIs(flights.time_conflict(6, 5), False)
        self.assertIs(flights.time_conflict(2, 7), False)


if __name__ == '__main__':
    unittest.main()
