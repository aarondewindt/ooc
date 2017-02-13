import os
import matplotlib.pyplot as plt

from ooc import BayGateSolver
from ooc.print_color import pr_g


def main():
    pr_g("Solving case for the 2nd of June 2015")

    solver = BayGateSolver(
        abs_path("jomo_kenyatta_international_airport"),
        abs_path("schedule_2015_06_02"),
        jid="workspace_2015_06_02"
    )

    # solver.solve_bay_assignment()
    solver.load_bay_assignment_solution()
    # solver.solve_gate_assignment()
    solver.load_gate_assignment_solution()
    solver.print_solution()
    bay_fig = solver.create_bay_assignment_chart()
    gate_fig = solver.create_gate_assignment_chart()

    plt.show()


    # pr_g("Solving case for the 5th of July 2015")
    # solver = BayGateSolver(
    #     abs_path("jomo_kenyatta_international_airport"),
    #     abs_path("schedule_2015_07_05"),
    #     jid="workspace_2015_07_05"
    # )
    #
    # solver.solve_bay_assignment()
    # solver.load_bay_assignment_solution()
    #
    # solver.solve_gate_assignment()
    # solver.load_gate_assignment_solution()
    #
    # solver.print_solution()


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.

    :param rel_path: Path relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


if __name__ == "__main__":
    main()