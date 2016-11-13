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
        assert airport.airlines["KQ"] == (0, "A")
        assert airport.airlines["G9"] == (1, "B")
        assert airport.airlines["EY"] == (1, "B")
        assert airport.airlines["SA"] == (2, "C")

    def test_load_aircraft(self):
        airport = Airport(abs_path("./airport_data"))

        assert airport.aircraft["B747"] == ("H", 400)
        assert airport.aircraft["B772"] == ("G", 300)
        assert airport.aircraft["B773"] == ("G", 300)
        assert airport.aircraft["B787"] == ("F", 200)
        assert airport.aircraft["B788"] == ("F", 200)
        assert airport.aircraft["A330"] == ("F", 200)
        assert airport.aircraft["B767"] == ("F", 200)
        assert airport.aircraft["B73J"] == ("E", 150)
        assert airport.aircraft["B737"] == ("D", 100)
        assert airport.aircraft["B738"] == ("D", 100)
        assert airport.aircraft["A320"] == ("D", 100)
        assert airport.aircraft["E90"] == ("C", 90)
        assert airport.aircraft["B733"] == ("B", 85)
        assert airport.aircraft["E70"] == ("B", 80)
        assert airport.aircraft["Q400"] == ("B", 50)
        assert airport.aircraft["AT4"] == ("A", 50)
        assert airport.aircraft["AT7"] == ("A", 50)

    def test_load_bay_compliance_matrix(self):
        airport = Airport(abs_path("./airport_data"))

        # There is no lazy way to generate a large list of asserts. So
        # I'll just a few random ones.
        # Test bay list
        assert airport.bay_names[0] == "2A"
        assert airport.bay_names[-1] == "H10"
        assert airport.bay_names[18] == "15"

        assert airport._bay_compliance_matrix[0]["H"] is False
        assert airport._bay_compliance_matrix[0]["A"] is True
        assert airport._bay_compliance_matrix[-1]["H"] is False
        assert airport._bay_compliance_matrix[-1]["A"] is True
        assert airport._bay_compliance_matrix[22]["H"] is True
        assert airport._bay_compliance_matrix[22]["A"] is False

    def test_load_bay_terminal_distance(self):
        airport = Airport(abs_path("./airport_data"))

        # Same as in test_load_bay_compliance_matrix, I'll just test a few cases.
        assert airport.terminal_names[0] == "A"
        assert airport.terminal_names[-1] == "D"

        self.assertAlmostEqual(airport._bay_terminal_distance[0]["A"], 19)
        self.assertAlmostEqual(airport._bay_terminal_distance[22]["C"], 18)
        self.assertAlmostEqual(airport._bay_terminal_distance[-1]["B"], 200)

    def test_load_domestic_airports(self):
        airport = Airport(abs_path("./airport_data"))
        assert "HOA" in airport.domestic_airports
        assert "GGM" in airport.domestic_airports
        assert "KLK" in airport.domestic_airports
        assert "KEY" in airport.domestic_airports
        assert "ILU" in airport.domestic_airports
        assert "KRV" in airport.domestic_airports
        assert "KIS" in airport.domestic_airports
        assert "KTL" in airport.domestic_airports
        assert "KWY" in airport.domestic_airports
        assert "LBN" in airport.domestic_airports
        assert "LAU" in airport.domestic_airports
        assert "LBK" in airport.domestic_airports
        assert "LOK" in airport.domestic_airports
        assert "LOY" in airport.domestic_airports
        assert "LKG" in airport.domestic_airports
        assert "MYD" in airport.domestic_airports
        assert "NDE" in airport.domestic_airports
        assert "RBT" in airport.domestic_airports
        assert "MRE" in airport.domestic_airports

    def test_terminal_bay_distance(self):
        airport = Airport(abs_path("./airport_data"))
        self.assertAlmostEqual(airport.terminal_bay_distance("A", 0), 19)

    def test_n_bays(self):
        airport = Airport(abs_path("./airport_data"))
        assert airport.n_bays == 46

    def test_n_gates(self):
        airport = Airport(abs_path("./airport_data"))
        assert airport.n_gates == 0
