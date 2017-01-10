import unittest
import os

from ooc import BayGateSolver


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.

    :param rel_path: Path relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


class TestBayGateSolver(unittest.TestCase):
    def test_solve_bay_assignment(self):
        solver = BayGateSolver(abs_path("./airport_data"),
                               abs_path("./flight_data"), "test_case")

        solver.solve_bay_assignment()
        solver.load_bay_assignment_solution()

        solver.solve_gate_assignment()
        solver.load_gate_assignment_solution()

        solver.print_solution()
