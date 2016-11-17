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

    def test_load_preferences(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)

        self.assertEquals(flights.adjacency[0], (8, 9))
        self.assertEquals(flights.adjacency[1], (13, 14))

    def test_n_flights(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.n_flights, 69)

    def test_n_passengers(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.n_passengers(0), 300)
        self.assertEquals(flights.n_passengers(40), 90)
        self.assertEquals(flights.n_passengers(60), 90)

    def test_airline(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.airline(0), "BA")
        self.assertEquals(flights.airline(5), "ET")

    def test_terminal(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.terminal(0), "A")
        self.assertEquals(flights.terminal(5), "C")

    def test_preference(self):
        # The preference function has to be implemented first.
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.preferences_table["KQ210"].dest, "BOM")
        self.assertEquals(flights.preferences_table["KQ210"].bays, (21,))
        self.assertEquals(flights.preferences_table["KQ210"].gates, (17,))
        self.assertEquals(flights.preferences_table["ET"].dest, "ADD")
        self.assertEquals(flights.preferences_table["ET"].bays, (11, 12))
        self.assertEquals(flights.preferences_table["ET"].gates, (7, 8))

    def test_load_adjacency(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertEquals(flights.adjacency, [(8, 9), (13, 14)])

    def test_domestic(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        self.assertIs(flights.domestic(0), False)
        self.assertIs(flights.domestic(48), True)

    def test_time_conflict(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)

        known_conflict = [(0, 21), (0, 24), (0, 47), (0, 48), (0, 50), (0, 62), (1, 4), (2, 36), (2, 52), (3, 14),
                          (5, 56), (8, 11), (9, 48), (13, 54), (16, 32), (17, 2), (17, 5), (17, 14), (17, 20), (17, 36),
                          (17, 44), (17, 52), (17, 53), (17, 68), (18, 6), (18, 34), (18, 35), (19, 52), (21, 35),
                          (21, 40), (21, 50), (21, 56), (24, 10), (24, 28), (24, 40), (24, 63), (24, 64), (27, 16),
                          (28, 26), (28, 38), (28, 46), (28, 66), (29, 61), (29, 67), (31, 36), (31, 43), (31, 52),
                          (31, 53), (31, 64), (32, 27), (32, 42), (33, 57), (34, 40), (34, 41), (34, 46), (35, 5),
                          (35, 18), (35, 21), (38, 1), (38, 5), (38, 21), (38, 25), (38, 40), (38, 41), (38, 46),
                          (38, 60), (38, 63), (39, 7), (39, 64), (40, 15), (40, 22), (40, 38), (40, 41), (40, 50),
                          (41, 15), (41, 24), (42, 27), (42, 29), (42, 51), (42, 67), (43, 36), (44, 4), (44, 14),
                          (45, 5), (45, 58), (46, 10), (46, 23), (46, 39), (46, 41), (46, 63), (46, 66), (47, 39),
                          (47, 63), (49, 12), (49, 61), (50, 47), (50, 63), (51, 32), (51, 49), (51, 67), (53, 20),
                          (53, 31), (53, 43), (57, 3), (57, 43), (57, 44), (58, 45), (59, 40), (61, 16), (61, 32),
                          (61, 51), (62, 0), (62, 21), (62, 41), (62, 46), (63, 38), (63, 48), (63, 62), (65, 20),
                          (65, 44), (65, 57), (65, 68), (66, 10), (66, 34), (66, 62)]

        known_non_conflict = [(0, 21), (0, 24), (0, 47), (0, 48), (0, 50), (0, 62), (1, 4), (2, 36), (2, 52), (3, 14),
                              (5, 56), (8, 11), (9, 48), (13, 54), (16, 32), (17, 2), (17, 5), (17, 14), (17, 20),
                              (17, 36), (17, 44), (17, 52), (17, 53), (17, 68), (18, 6), (18, 34), (18, 35), (19, 52),
                              (21, 35), (21, 40), (21, 50), (21, 56), (24, 10), (24, 28), (24, 40), (24, 63), (24, 64),
                              (27, 16), (28, 26), (28, 38), (28, 46), (28, 66), (29, 61), (29, 67), (31, 36), (31, 43),
                              (31, 52), (31, 53), (31, 64), (32, 27), (32, 42), (33, 57), (34, 40), (34, 41), (34, 46),
                              (35, 5), (35, 18), (35, 21), (38, 1), (38, 5), (38, 21), (38, 25), (38, 40), (38, 41),
                              (38, 46), (38, 60), (38, 63), (39, 7), (39, 64), (40, 15), (40, 22), (40, 38), (40, 41),
                              (40, 50), (41, 15), (41, 24), (42, 27), (42, 29), (42, 51), (42, 67), (43, 36), (44, 4),
                              (44, 14), (45, 5), (45, 58), (46, 10), (46, 23), (46, 39), (46, 41), (46, 63), (46, 66),
                              (47, 39), (47, 63), (49, 12), (49, 61), (50, 47), (50, 63), (51, 32), (51, 49), (51, 67),
                              (53, 20), (53, 31), (53, 43), (57, 3), (57, 43), (57, 44), (58, 45), (59, 40), (61, 16),
                              (61, 32), (61, 51), (62, 0), (62, 21), (62, 41), (62, 46), (63, 38), (63, 48), (63, 62),
                              (65, 20), (65, 44), (65, 57), (65, 68), (66, 10), (66, 34), (66, 62)]

        for i in range(flights.n_flights):
            for j in range(flights.n_flights):
                if ((i, j) in known_conflict) or ((i, j) in known_non_conflict):
                    if flights.time_conflict(i, j):
                        self.assertIn((i, j), known_conflict)
                    else:
                        self.assertIn((i, j), known_non_conflict)


if __name__ == '__main__':
    unittest.main()
