"""
These tests are used to test the Airport class used to load in and process the airport information.
"""

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
        self.assertEquals(airport.airlines["KQ"], (999, "A"))
        self.assertEquals(airport.airlines["G9"], (999, "B"))
        self.assertEquals(airport.airlines["EY"], (999, "C"))
        self.assertEquals(airport.airlines["SA"], (999, "B"))

    def test_load_aircraft(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertEquals(airport.aircraft["B747"], ("H", 660))
        self.assertEquals(airport.aircraft["B772"], ("G", 440))
        self.assertEquals(airport.aircraft["B773"], ("G", 550))
        self.assertEquals(airport.aircraft["B787"], ("F", 250))
        self.assertEquals(airport.aircraft["B788"], ("F", 290))
        self.assertEquals(airport.aircraft["A330"], ("F", 335))
        self.assertEquals(airport.aircraft["A332"], ("F", 253))
        self.assertEquals(airport.aircraft["B767"], ("F", 375))
        self.assertEquals(airport.aircraft["B73J"], ("E", 132))
        self.assertEquals(airport.aircraft["B737"], ("D", 132))
        self.assertEquals(airport.aircraft["B738"], ("D", 189))
        self.assertEquals(airport.aircraft["A320"], ("D", 180))
        self.assertEquals(airport.aircraft["E90"], ("C", 114))
        self.assertEquals(airport.aircraft["CRJ9"], ("B", 90))
        self.assertEquals(airport.aircraft["B733"], ("B", 137))
        self.assertEquals(airport.aircraft["E70"], ("B", 78))
        self.assertEquals(airport.aircraft["Q400"], ("B", 78))
        self.assertEquals(airport.aircraft["AT4"], ("A", 52))
        self.assertEquals(airport.aircraft["AT7"], ("A", 72))

    def test_load_bay_compliance_matrix(self):
        airport = Airport(abs_path("./airport_data"))

        # There is no lazy way to generate a large list of asserts. So
        # I'll just a few random ones.
        # Test bay list
        self.assertEquals(airport.bay_names[0], "2A")
        self.assertEquals(airport.bay_names[-1], "SPV2")
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
        self.assertAlmostEqual(airport._bay_terminal_distance[-1]["B"], 100)

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
        self.assertEquals(airport.n_bays, 48)

    def test_n_gates(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertEquals(airport.n_gates, 23)

    def test_bay_gate_distance(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertEquals(airport.n_gates, 23)
        k, l = 14, 22
        print(airport.bay_names[k], airport.gate_names[l], airport.bay_gate_distance[k][l])
        self.assertAlmostEquals(airport.bay_gate_distance[26][13], 742.0)
        self.assertAlmostEquals(airport.bay_gate_distance[14][22], 279.0)

    def test_load_remote_bays(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertIn(24, airport.remote_bays)
        self.assertIn(25, airport.remote_bays)
        self.assertIn(26, airport.remote_bays)
        self.assertIn(33, airport.remote_bays)
        self.assertIn(35, airport.remote_bays)

    def test_load_adjacency(self):
        """
        Checks whether the adjacency matrix has been loaded correctly.
        """
        airport = Airport(abs_path("./airport_data"))

        self.assertEquals(airport.adjacency[0], (8, 9))
        self.assertEquals(airport.adjacency[1], (13, 14))
