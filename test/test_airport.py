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
        airport = Airport(abs_path("./airport_data"))
        self.assertEquals(airport.airlines["KQ"], (0, "A"))
        self.assertEquals(airport.airlines["G9"], (1, "B"))
        self.assertEquals(airport.airlines["EY"], (2, "C"))
        self.assertEquals(airport.airlines["SA"], (3, "D"))

    def test_load_aircraft(self):
        airport = Airport(abs_path("./airport_data"))

        self.assertEquals(airport.aircraft["747"], ("H", 400))
        self.assertEquals(airport.aircraft["772"], ("G", 300))
        self.assertEquals(airport.aircraft["773"], ("G", 300))
        self.assertEquals(airport.aircraft["787"], ("F", 200))
        self.assertEquals(airport.aircraft["788"], ("F", 200))
        self.assertEquals(airport.aircraft["A330"], ("F", 200))
        self.assertEquals(airport.aircraft["767"], ("F", 200))
        self.assertEquals(airport.aircraft["73J"], ("E", 150))
        self.assertEquals(airport.aircraft["737"], ("D", 100))
        self.assertEquals(airport.aircraft["738"], ("D", 100))
        self.assertEquals(airport.aircraft["A320"], ("D", 100))
        self.assertEquals(airport.aircraft["E90"], ("C", 90))
        self.assertEquals(airport.aircraft["733"], ("B", 85))
        self.assertEquals(airport.aircraft["E70"], ("B", 80))
        self.assertEquals(airport.aircraft["Q400"], ("B", 50))
        self.assertEquals(airport.aircraft["AT4"], ("A", 50))
        self.assertEquals(airport.aircraft["AT7"], ("A", 50))

    def test_load_bay_compliance_matrix(self):
        airport = Airport(abs_path("./airport_data"))

        # There is no lazy way to generate a large list of asserts. So
        # I'll just a few random ones.
        # Test bay list
        self.assertEquals(airport.bay_names[0], "2A")
        self.assertEquals(airport.bay_names[-1], "H10")
        self.assertEquals(airport.bay_names[18], "15")

        self.assertIs(airport.bay_compliance_matrix[0]["H"], False)
        self.assertIs(airport.bay_compliance_matrix[0]["A"], True)
        self.assertIs(airport.bay_compliance_matrix[-1]["H"], False)
        self.assertIs(airport.bay_compliance_matrix[-1]["A"], True)
        self.assertIs(airport.bay_compliance_matrix[22]["H"], True)
        self.assertIs(airport.bay_compliance_matrix[22]["A"], False)

    def test_load_bay_terminal_distance(self):
        airport = Airport(abs_path("./airport_data"))

        # Same as in test_load_bay_compliance_matrix, I'll just test a few cases.
        self.assertEquals(airport.terminal_names[0], "A")
        self.assertEquals(airport.terminal_names[-1], "D")

        self.assertAlmostEqual(airport._bay_terminal_distance[0]["A"], 19)
        self.assertAlmostEqual(airport._bay_terminal_distance[22]["C"], 18)
        self.assertAlmostEqual(airport._bay_terminal_distance[-1]["B"], 200)

    def test_load_domestic_airports(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertIn("HOA", airport.domestic_airports)
        self.assertIn("GGM", airport.domestic_airports)
        self.assertIn("KLK", airport.domestic_airports)
        self.assertIn("KEY", airport.domestic_airports)
        self.assertIn("ILU", airport.domestic_airports)
        self.assertIn("KRV", airport.domestic_airports)
        self.assertIn("KIS", airport.domestic_airports)
        self.assertIn("KTL", airport.domestic_airports)
        self.assertIn("KWY", airport.domestic_airports)
        self.assertIn("LBN", airport.domestic_airports)
        self.assertIn("LAU", airport.domestic_airports)
        self.assertIn("LBK", airport.domestic_airports)
        self.assertIn("LOK", airport.domestic_airports)
        self.assertIn("LOY", airport.domestic_airports)
        self.assertIn("LKG", airport.domestic_airports)
        self.assertIn("MYD", airport.domestic_airports)
        self.assertIn("NDE", airport.domestic_airports)
        self.assertIn("RBT", airport.domestic_airports)
        self.assertIn("MRE", airport.domestic_airports)

    def test_load_fueling(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertIs(airport.fueling[0], True)
        self.assertIs(airport.fueling[33], False)

    def test_load_gates(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertIn("18", airport.gate_names)

    def test_max_distance(self):
        airport = Airport(abs_path("./airport_data"))

        print(airport.max_distance)

    def test_terminal_bay_distance(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertAlmostEqual(airport.terminal_bay_distance("A", 0), 19)

    def test_n_bays(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertEquals(airport.n_bays, 46)

    def test_n_gates(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertEquals(airport.n_gates, 0)
