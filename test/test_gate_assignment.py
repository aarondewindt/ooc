import unittest
import os

from ooc import Airport, Flights, GateAssignment


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.

    :param rel_path: PAth relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


class TestGateAssignment(unittest.TestCase):
    @staticmethod
    def load_small_case():
        """
        This is not a unit test. This function is used to load in the small flight schedule case.
        :return:
        """

        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        bay_solution = [11, 8, 8, 8, 14, 14, 14, 16, 17]
        return GateAssignment(flights, bay_solution)

    def test_of_min_bay_gate_distance(self):
        gate_assignment = self.load_small_case()
        print(gate_assignment.of_min_bay_gate_distance())

    def test_of_airline_preference(self):
        gate_assignment = self.load_small_case()
        # The list of feasible decision variables (flight, gate combination) is defined in this
        # function. So it's the first function that must run.
        gate_assignment.of_min_bay_gate_distance()

        print(gate_assignment.of_airline_preference())

    def test_of_penalty_variables(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()
        gate_assignment.constraint_time_conflict()
        print(gate_assignment.of_penalty_variables())

    def test_binary_decision_variables_declaration(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()

        print(gate_assignment.binary_decision_variables_declaration())

    def test_constraint_single_gate_per_flight(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()

        print(gate_assignment.constraint_single_gate_per_flight())

    def test_constraint_max_two_flights_per_gate(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()
        print(gate_assignment.constraint_time_conflict())

    def test_constraint_domestic(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()
        print(gate_assignment.constraint_domestic())

    def test_constraint_kq_after_6pm(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()
        print(gate_assignment.constraint_kq_after_6pm())

    def test_lp_code(self):
        gate_assignment = self.load_small_case()
        print(gate_assignment.lp_code())
