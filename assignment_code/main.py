import os
import matplotlib.pyplot as plt
from datetime import timedelta

from ooc import BayGateSolver
from ooc.print_color import pr_g


def main():
    pr_g("Solving case for the 2nd of June 2015")

    solver = BayGateSolver(
        abs_path("jomo_kenyatta_international_airport"),
        abs_path("schedule_2015_06_02"),
        jid="workspace_2015_06_02",
        buffer_time=timedelta(minutes=15),
        spare_bays=['J2A', 'J2B'],
    )

    # solver.solve_bay_assignment()
    solver.load_bay_assignment_solution()
    # solver.solve_gate_assignment()
    solver.load_gate_assignment_solution()
    solver.print_solution()
    solver.save_csv()
    bay_fig = solver.create_bay_assignment_chart("Bay assignment for the 2nd of June 2015")
    gate_fig = solver.create_gate_assignment_chart("Gate assignment for the 2nd of June 2015")

    # pr_g("Solving case for the 5th of July 2015")
    # solver = BayGateSolver(
    #     abs_path("jomo_kenyatta_international_airport"),
    #     abs_path("schedule_2015_07_05"),
    #     jid="workspace_2015_07_05",
    #     buffer_time=timedelta(minutes=15),
    #     spare_bays=['J3A', 'J3B']
    # )
    #
    # solver.solve_bay_assignment()
    # solver.load_bay_assignment_solution()
    # # solver.solve_gate_assignment()
    # # solver.load_gate_assignment_solution()
    #
    # solver.print_solution()
    # solver.save_csv()
    # bay_fig = solver.create_bay_assignment_chart("Bay assignment for the 5th of July 2015")
    # # gate_fig = solver.create_gate_assignment_chart("Gate assignment for the 2nd of June 2015")
    # #
    # plt.show()


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.

    :param rel_path: Path relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


if __name__ == "__main__":
    main()
