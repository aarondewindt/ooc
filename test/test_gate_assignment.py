"""
These unittest make sure that nothing is accidentally changed to the gate assignment code.
The code was first manually checked by printing it out on the console. Once done, the correct results
where stored in a file and the generated code is then checked against the those.
"""

import unittest
import os
import pickle

from ooc import Airport, Flights, GateAssignment


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.

    :param rel_path: PAth relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


RESET_CORRECT = False


def set_correct(key, value):
    if not RESET_CORRECT:
        return

    file_path = abs_path("gate_test_correct.pickle")
    if os.path.isfile(file_path):
        with open(file_path, "rb") as f:
            data = pickle.load(f)
    else:
        data = {}
    data[key] = value
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


def get_correct(key):
    with open(abs_path("gate_test_correct.pickle"), "rb") as f:
        data = pickle.load(f)
        return data[key]


class TestGateAssignment(unittest.TestCase):
    @staticmethod
    def load_small_case():
        """
        This is not a unit test. This function is used to load in the small flight schedule case.
        :return:
        """

        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data_small"), airport)
        bay_solution = ["11", "8", "8", "8", "14", "14", "14", "16", "2B", "4L", "3B", "3C", "16"]
        for i, bay_name in enumerate(bay_solution):
            if bay_name in airport.bay_names:
                bay_solution[i] = airport.bay_names.index(bay_name)

        return GateAssignment(flights, bay_solution)

    def test_of_min_bay_gate_distance(self):
        gate_assignment = self.load_small_case()
        code = gate_assignment.of_min_bay_gate_distance()
        print(code)
        set_correct("gate_assignment.of_min_bay_gate_distance", code)
        self.assertEqual(get_correct("gate_assignment.of_min_bay_gate_distance"), code)

    def test_of_airline_preference(self):
        gate_assignment = self.load_small_case()
        # The list of feasible decision variables (flight, gate combination) is defined in this
        # function. So it's the first function that must run.
        gate_assignment.of_min_bay_gate_distance()

        code = gate_assignment.of_airline_preference()
        print(code)
        set_correct("gate_assignment.of_airline_preference", code)
        self.assertEqual(get_correct("gate_assignment.of_airline_preference"), code)

    def test_of_penalty_variables(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()
        gate_assignment.constraint_time_conflict()
        code = gate_assignment.of_penalty_variables()
        print(code)
        set_correct("gate_assignment.of_penalty_variables", code)
        self.assertEqual(get_correct("gate_assignment.of_penalty_variables"), code)

    def test_binary_decision_variables_declaration(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()

        code = gate_assignment.binary_decision_variables_declaration()
        print(code)
        set_correct("gate_assignment.binary_decision_variables_declaration", code)
        self.assertEqual(get_correct("gate_assignment.binary_decision_variables_declaration"), code)

    def test_constraint_single_gate_per_flight(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()

        code = gate_assignment.constraint_single_gate_per_flight()
        print(code)
        set_correct("gate_assignment.constraint_single_gate_per_flight", code)
        self.assertEqual(get_correct("gate_assignment.constraint_single_gate_per_flight"), code)

    def test_constraint_max_two_flights_per_gate(self):
        gate_assignment = self.load_small_case()
        gate_assignment.of_min_bay_gate_distance()
        code = gate_assignment.constraint_time_conflict()
        print(code)
        set_correct("gate_assignment.constraint_time_conflict", code)
        self.assertEqual(get_correct("gate_assignment.constraint_time_conflict"), code)

    # Not used anymore
    # def test_constraint_domestic(self):
    #     gate_assignment = self.load_small_case()
    #     gate_assignment.of_min_bay_gate_distance()
    #     code = gate_assignment.constraint_domestic()
    #     print(code)
    #     set_correct("gate_assignment.constraint_domestic", code)
    #     self.assertEqual(get_correct("gate_assignment.constraint_domestic"), code)
    #
    # def test_constraint_kq_after_6pm(self):
    #     gate_assignment = self.load_small_case()
    #     gate_assignment.of_min_bay_gate_distance()
    #     code = gate_assignment.constraint_kq_after_6pm()
    #     print(code)
    #     set_correct("gate_assignment.constraint_kq_after_6pm", code)
    #     self.assertEqual(get_correct("gate_assignment.constraint_kq_after_6pm"), code)

    def test_lp_code(self):
        gate_assignment = self.load_small_case()
        code = gate_assignment.lp_code()
        print(code)
        set_correct("gate_assignment.lp_code", code)
        self.assertEqual(get_correct("gate_assignment.lp_code"), code)
