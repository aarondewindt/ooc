import unittest
import os
import datetime

from ooc import Flights, Airport, ft


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.

    :param rel_path: Path relative to this file
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
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.flight_schedule[0].flight_type, ft.Full)
        self.assertEquals(flights.flight_schedule[0][0], ft.Full)
        self.assertEquals(flights.flight_schedule[0].eta, datetime.datetime(2015, 6, 2, 20, 30))
        self.assertEquals(flights.flight_schedule[6].flight_type, ft.Dep)
        self.assertEquals(flights.flight_schedule[6].ac_type, "E90")
        self.assertIsNone(flights.flight_schedule[5].in_flight_no)
        self.assertEquals(flights.flight_schedule[0].in_flight_no, "BA065")
        self.assertEquals(flights.flight_schedule[7].in_flight_no, "KQ419")

    def test_process_overnight_flights(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.flight_schedule[4].eta, datetime.datetime(2015, 6, 1, 21, 15))
        self.assertEquals(flights.flight_schedule[4].etd, datetime.datetime(2015, 6, 1, 22, 39))
        self.assertEquals(flights.flight_schedule[5].eta, datetime.datetime(2015, 6, 1, 22, 45))
        self.assertEquals(flights.flight_schedule[5].etd, datetime.datetime(2015, 6, 2,  5, 14))
        self.assertEquals(flights.flight_schedule[6].eta, datetime.datetime(2015, 6, 2,  5, 20))
        self.assertEquals(flights.flight_schedule[6].etd, datetime.datetime(2015, 6, 2,  6, 50))

    def test_n_flights(self):
        """
        Check if the number of flights loaded in is correct.

        :return:
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.n_flights, 13)

    def test_n_passengers(self):
        """
        Checks whether the number of passengers for each flight is correct.

        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.n_passengers(0), 440)
        self.assertEquals(flights.n_passengers(3), 189)
        self.assertEquals(flights.n_passengers(7), 114)

    def test_airline(self):
        """
        Checks whether the airline detection code is working.

        :return:
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.airline(0), "BA")
        self.assertEquals(flights.airline(5), "KQ")

    def test_terminal(self):
        """
        Checks whether the correct terminal has been found for the flights.
        :return:
        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.terminal(0), "C")
        self.assertEquals(flights.terminal(3), "C")

    def test_preference(self):
        """
        Checks whether the preference table has been loaded in correctly.
        """
        # The preference function has to be implemented first.
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertEquals(flights.preferences_table["KQ210"].dest, "BOM")
        self.assertEquals(flights.preferences_table["KQ210"].bays, (21,))
        self.assertEquals(flights.preferences_table["KQ210"].gates, (15,))
        self.assertEquals(flights.preferences_table["ET"].dest, "ADD")
        self.assertEquals(flights.preferences_table["ET"].bays, (11, 12))
        self.assertEquals(flights.preferences_table["ET"].gates, (6, 7))

    def test_domestic(self):
        """
        Checks whether domestic flights are detected correctly.

        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        self.assertIs(flights.domestic(0), False)
        self.assertIs(flights.domestic(6), True)

    def test_time_conflict(self):
        """
        Checks whether the time conflict function works correctly.

        """
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)

        self.assertIs(flights.time_conflict(6, 7), True)
        self.assertIs(flights.time_conflict(8, 9), True)

        self.assertIs(flights.time_conflict(0, 4), False)
        self.assertIs(flights.time_conflict(0, 2), False)
        self.assertIs(flights.time_conflict(7, 8), False)

    def test_is_overnight(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)

        self.assertIs(flights.is_overnight(0), False)
        self.assertIs(flights.is_overnight(4), True)
        self.assertIs(flights.is_overnight(5), True)
        self.assertIs(flights.is_overnight(6), True)
        self.assertIs(flights.is_overnight(2), False)

if __name__ == '__main__':
    unittest.main()
