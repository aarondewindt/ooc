"""
This is the main entry file for the assignment.
"""

import sys
import os
import matplotlib.pyplot as plt
from datetime import timedelta
from ooc import BayGateSolver
from ooc.print_color import pr_g

# True to only show the last calculated results.
# To run the optimizations code it must be set to False
only_show_results = True


def main():
    # Solve the two cases and get the figures.
    case_1_figs = solve_2nd_of_june_2015()
    case_2_figs = solve_5th_of_july_2015()

    # Show the figures.
    plt.show()


def solve_2nd_of_june_2015():
    pr_g("Solving case for the 2nd of June 2015")

    solver = BayGateSolver(
        abs_path("jomo_kenyatta_international_airport"),
        abs_path("schedule_2015_06_02"),
        jid="workspace_2015_06_02",

        # This is 15 min buffer time before and after each flight. So 30 min between flights.
        buffer_time=timedelta(minutes=15),
        spare_bays=['J2A', 'J2B'],
    )

    bay_dt_cg, bay_dt_sl = solver.solve_bay_assignment() if not only_show_results else None, None
    solver.load_bay_assignment_solution()

    gate_dt_cg, gate_dt_sl = solver.solve_gate_assignment() if not only_show_results else None, None
    solver.load_gate_assignment_solution()

    solver.print_solution()
    solver.save_csv()
    bay_fig = solver.create_bay_assignment_chart("Bay assignment for the 2nd of June 2015")
    gate_fig = solver.create_gate_assignment_chart("Gate assignment for the 2nd of June 2015")

    print("Bay assignment code generation time  {}".format(bay_dt_cg))
    print("Bay assignment cplex execution time  {}".format(bay_dt_sl))
    print("Gate assignment code generation time {}".format(gate_dt_cg))
    print("Gate assignment cplex execution time {}".format(gate_dt_sl))

    return bay_fig, gate_fig


def solve_5th_of_july_2015():
    pr_g("Solving case for the 5th of July 2015")
    solver = BayGateSolver(
        abs_path("jomo_kenyatta_international_airport"),
        abs_path("schedule_2015_07_05"),
        jid="workspace_2015_07_05",
        buffer_time=timedelta(minutes=15),
        spare_bays=['J3A', 'J3B']
    )

    bay_dt_cg, bay_dt_sl = solver.solve_bay_assignment() if not only_show_results else None, None
    solver.load_bay_assignment_solution()

    gate_dt_cg, gate_dt_sl = solver.solve_gate_assignment() if not only_show_results else None, None
    solver.load_gate_assignment_solution()

    solver.print_solution()
    solver.save_csv()
    bay_fig = solver.create_bay_assignment_chart("Bay assignment for the 5th of July 2015")
    gate_fig = solver.create_gate_assignment_chart("Gate assignment for the 5th of July 2015")

    print("Bay assignment code generation time  {}".format(bay_dt_cg))
    print("Bay assignment cplex execution time  {}".format(bay_dt_sl))
    print("Gate assignment code generation time {}".format(gate_dt_cg))
    print("Gate assignment cplex execution time {}".format(gate_dt_sl))

    return bay_fig, gate_fig


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.

    :param rel_path: Path relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


if __name__ == "__main__":
    # Add the repository root to the python path in order to make the ooc package available for import.
    sys.path.append(abs_path(".."))

    # Run the main function.
    main()
