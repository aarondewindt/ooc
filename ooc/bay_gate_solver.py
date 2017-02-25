"""
This is the main interface of the package. The class in here creates the necessary instance of the Airport, Flight
BayAssignment and GateAssignment classes, runs all of them and processes the results.
"""

from os import mkdir, remove
from os.path import isdir, isfile, abspath, normpath, join
import subprocess
import sys
import xml.etree.ElementTree as ET  #: the extra-terrestrial
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from time import perf_counter

from ooc import print_color
from ooc import Airport, Flights, BayAssignment, FlightSolution, GateAssignment, ft
from ooc.key_pair_dictionary import KeyPairDictionary

colors = [
    ("#1f77b4", "#66b0e5"),  # 0 Blue
    ("#17becf", "#5edfed"),  # 1 Cyan
    ("#bcbd22", "#e4e467"),  # 2 Olive
    ("#8c564b", "#c1948b"),  # 3 Brown
    ("#ff7f0e", "#ffa04d"),  # 4 Orange
    ("#d62728", "#e36868"),  # 5 Red
    ("#7f7f7f", "#a6a6a6"),  # 6 Grey
    ("#2ca02c", "#73d973"),  # 7 Green
    ("#9467bd", "#b395d0"),  # 8 Purple
    ("#e377c2", "#eeaad9"),  # 9 Pink
]
"""
List of colors with dark and light version of each. Used for plotting.
"""


class BayGateSolver:
    """
    This class is used to generate and solve the bay and gate assignment
    problems.

    :param string airport_path: Path to directory holding the airport data
    :param string flights_path: Path to directory holding the flights data.
    :param string cplex_command: Terminal command to access the cplex interactive solver.
    :param datetime.timedelta buffer_time: Amount of buffer time to add before and after
       each flight.
    :param list spare_bays: List of strings with the names of the spare bays.
    :param int line_width_limit: Line width limit for the generated LP code. Note since the line
       width is checked after appending, the code might exceed this limit with a few characters.
    """

    def __init__(self, airport_data_path, flights_data_path, jid, cplex_command="cplex", buffer_time=None,
                 spare_bays=None, line_width_limit=120):
        self.line_width_limit = line_width_limit

        self.airport = Airport(airport_data_path=airport_data_path)
        """"
        class:`ooc.Airport` object of holding the information of
        the target airport.
        """

        self.flights = Flights(flight_data_path=flights_data_path, airport=self.airport, buffer_time=buffer_time,
                               spare_bays=spare_bays)
        """
        class:`ooc.Flights` object holding the information of all
        flights of the day
        """

        self.jid = jid
        """
        Job id. This is a unique id for a specific run or set of runs. The workspace
        folder will be named after the jid.
        """

        self.workspace_path = abspath("./" + self.jid)
        """
        Path to directory which will hold all of the generated lp files ond solutions.
        """

        self.solutions = []  # List holding the final solution.

        self.init_workspace()  # Initialize workspace.
        self.init_solution_list()

        # Create a few path to relevant paths.
        self.bay_lp_path = normpath(join(self.workspace_path, "bay.lp"))
        self.bay_sol_path = normpath(join(self.workspace_path, "bay.sol"))
        self.gate_lp_path = normpath(join(self.workspace_path, "gate.lp"))
        self.gate_sol_path = normpath(join(self.workspace_path, "gate.sol"))
        self.result_path = normpath(join(self.workspace_path, "result.csv"))

        # Check whether we can access cplex from the command line.
        try:
            # For some reason the 'subprocess.run' function does not work like described in the documentation in
            # linux. So after some trail and error I got it working by giving it a list with
            if sys.platform == "linux":
                args = [cplex_command + " -c help"]
            else:  # This works on Windows. Probably also MAC since this is the behaviour described in the documentation
                args = [cplex_command, "-c", "help"]
            result = subprocess.run(args,
                                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # We can. Store command for later use.
            if len(result.stderr):
                print_color.pr_r(
                    "Warning: Cplex was not found. Please check whether the cplex command is correct. Otherwise cplex "
                    "will have to be run separately.")
                self.cplex_command = None
            else:
                self.cplex_command = cplex_command
        except OSError:
            # We can't. We'll have to run the solver manually.
            print_color.pr_r(
                "Warning: Cplex was not found. Please check whether the cplex command is correct. Otherwise cplex "
                "will have to be run separately.")
            self.cplex_command = None

    def init_workspace(self):
        """
        This function initializes the workspace directory used to store the generated code files and results.
        """

        # Create the directory if it doesn't exist yet.
        if not isdir(self.workspace_path):
            mkdir(self.workspace_path)

        # Create a .gitignore file in the workspace directory in order to let git know
        # it has to ignore all the generated files in there.
        if not isfile(join(self.workspace_path, ".gitignore")):
            with open(join(self.workspace_path, ".gitignore"), "w") as f:
                # For now ignore everything. At some point I'm gonna change this so it keeps
                # the final results.
                f.write("""*.log""")

    def init_solution_list(self):
        """
        Initializes the list that will hold the solution eventually.
        """
        for i, flight in enumerate(self.flights.flight_schedule):
            solution = FlightSolution(i, self)
            self.solutions.append(solution)

            solution.flight_type = flight.flight_type
            solution.in_flight_no = flight.in_flight_no
            solution.origin = flight.origin
            solution.eta = flight.eta
            solution.reg_no = flight.reg_no
            solution.out_flight_no = flight.out_flight_no
            solution.dest = flight.dest
            solution.etd = flight.etd
            solution.ac_type = flight.ac_type
            solution.pref = flight.preference

    def solve_bay_assignment(self):
        """
        Generates the lp code needed to solve the bay assignment,
        solves it using cplex and loads in the solution.
        """
        t0 = perf_counter()
        bay_assignment = BayAssignment(self.flights, line_width_limit=self.line_width_limit)

        # Generate and save lp code.
        with open(self.bay_lp_path, "w") as f:
            f.write(bay_assignment.lp_code())
        dt_code_generation = perf_counter() - t0
        dt_solving = 0

        if self.cplex_command is not None:
            print("Solving bay assignment with cplex...")
            # Remove old solution file
            if isfile(self.bay_sol_path):
                remove(self.bay_sol_path)

            # Try to solve it.
            # For some reason the 'subprocess.run' function does not work like described in the documentation in
            # linux. So after some trail and error I got it working by giving it a list with
            if sys.platform == "linux":
                args = [self.cplex_command + " -c 'read {}' optimize 'write {}'".format(
                self.bay_lp_path, self.bay_sol_path
            )]
            else:  # This works on Windows. Probably also MAC since this is the behaviour described in the documentation
                args = [
                    self.cplex_command,
                    "-c",
                    "read {}".format(self.bay_lp_path,),
                    "optimize",
                    "write {}".format(self.bay_sol_path)]
            t0 = perf_counter()
            subprocess.run(args,
                           shell=True,)
            dt_solving = perf_counter() - t0

            if not isfile(self.bay_sol_path):
                raise Exception("No solution file was generated for the bay assignment.")

            print("Bay assignment solved\n")
        else:
            print("Cplex is not available in the command line.\n"
                  "The bay assignment lp code was generated and saved at\n{}\n".format(self.bay_lp_path) +
                  "Please solve it in cplex and save the resulting .sol (xml) file at\n{}\n".format(self.bay_sol_path))

        return dt_code_generation, dt_solving

    def load_bay_assignment_solution(self):
        # Check whether there is a solution file in the workspace.
        if not isfile(self.bay_sol_path):
            raise Exception("No bay assignment solution file was found at {}.".format(self.bay_sol_path))

        # Load in xml file outputted by cplex
        CPLEXSolution = ET.parse(self.bay_sol_path).getroot()

        variable_elements = CPLEXSolution.findall("variables/variable")
        for element in variable_elements:
            # Check whether the variable element is for one of the X decision variables.
            name = element.get("name")
            if name.startswith("X"):
                _, i, k = name.split("_")
                i = int(i)  # Flight index
                k = int(k)  # Bay index
                assigned = bool(round(float(element.get("value"))))  # If True, than flight i has been assigned to bay k
                if assigned:
                    if self.solutions[i].bay_idx is None:
                        self.solutions[i].bay_idx = k
                        self.solutions[i].bay = self.airport.bay_names[k]
                    else:
                        # Sanity check while developing.
                        raise Exception("Flight {} has been assigned to two bays.".format(i))

        # Check whether there is a solution for all flights.
        for i, solution in enumerate(self.solutions):
            assert solution.bay is not None, "Flight {} has no bay assigned to it.".format(i)

    def solve_gate_assignment(self):
        t0 = perf_counter()

        bays = [solution.bay_idx for solution in self.solutions]
        if bays[0] is None:
            raise Exception("No bay assignment solutions has been loaded.")

        gate_assignment = GateAssignment(self.flights, bays, line_width_limit=self.line_width_limit)

        # Generate and save lp code.
        with open(self.gate_lp_path, "w") as f:
            f.write(gate_assignment.lp_code())

        dt_code_generation = perf_counter() - t0
        dt_solving = 0

        if self.cplex_command is not None:
            print("Solving gate assignment with cplex...")
            # Remove old solution file
            if isfile(self.gate_sol_path):
                remove(self.gate_sol_path)

            # Try to solve it.
            # For some reason the 'subprocess.run' function does not work like described in the documentation in
            # linux. So after some trail and error I got it working by giving it a list with
            if sys.platform == "linux":
                args = [self.cplex_command + " -c 'read {}' optimize 'write {}'".format(
                self.gate_lp_path, self.gate_sol_path)]
            else:  # This works on Windows. Probably also MAC since this is the behaviour described in the documentation
                args = [
                    self.cplex_command,
                    "-c",
                    "read {}".format(self.gate_lp_path,),
                    "optimize",
                    "write {}".format(self.gate_sol_path)]

            try:
                t0 = perf_counter()
                subprocess.run(args,
                               shell=True)
                dt_solving = perf_counter() - t0
            except KeyboardInterrupt:
                # By handling this exception we can cancel cplex and get the intermediate solution.
                pass

            if not isfile(self.gate_sol_path):
                raise Exception("No solution file was generated for the gate assignment.")

            print("Gate assignment solved\n")
        else:
            print("Cplex is not available in the command line.\n"
                  "The gate assignment lp code was generated and saved at\n{}\n".format(self.gate_lp_path) +
                  "Please solve it in cplex and save the resulting .sol (xml) file at\n{}\n".format(self.gate_sol_path))

        return dt_code_generation, dt_solving

    def load_gate_assignment_solution(self):
        # Check whether there is a solution file in the workspace.
        if not isfile(self.gate_sol_path):
            raise Exception("No gate assignment solution file was found at {}.".format(self.bay_sol_path))

        # Load in xml file outputted by cplex
        CPLEXSolution = ET.parse(self.gate_sol_path).getroot()

        variable_elements = CPLEXSolution.findall("variables/variable")
        for element in variable_elements:
            # Check whether the variable element is for one of the X decision variables.
            name = element.get("name")
            if name.startswith("X"):
                _, i, l = name.split("_")
                i = int(i)  # Flight index
                l = int(l)  # Gate index
                assigned = bool(round(float(element.get("value"))))  # If True, than flight i has been assigned to bay k.
                if assigned:
                    # Check that no gate has been assigned to this flight yet.
                    if self.solutions[i].gate_idx is None:
                        self.solutions[i].gate_idx = l
                        self.solutions[i].gate = self.airport.gate_names[l]
                    else:
                        # Throw an error if a gate has already been assigned.
                        raise Exception("Flight {} has been assigned to two gates.".format(i))

        # Sanity check
        # Check whether there is a solution for all flights.
        for i, solution in enumerate(self.solutions):
            if self.flights.departing(i):
                assert solution.bay is not None, "Flight {} has no bay assigned to it.".format(i)

    def print_solution(self):
        """
        Returns a string with the solutions

        :return:
        """
        # Get the table header.
        s = self.solutions[0].str_heading()

        # Loop through each solution to get it's values.
        for solution in self.solutions:
            s += solution.str_data()

        # Print the table to the console.
        print(s)

    def save_csv(self):
        """
        Saves the result to a csv file in the workspace directory named 'result.csv'.

        :return:
        """

        # Get the csv table header.
        s = self.solutions[0].csv_heading()

        # Loop through each solution to get it's values
        for solution in self.solutions:
            s += solution.csv_data()

        # Open the csv file and write the table to it.
        with open(self.result_path, "w") as f:
            f.write(s)

    def create_bay_assignment_chart(self, title):
        # Create a new figure.
        fig = plt.figure(figsize=(8, 8))

        # Set the y-axis tick labels to bay names
        plt.yticks(range(self.airport.n_bays), self.airport.bay_names)

        # Format the x-axis so it displays the time of the day.
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())
        plt.ylim([-1, self.airport.n_bays])

        reposition_idx = 0

        # Loop through each solution
        for i, solution in enumerate(self.solutions):
            # Set the color based on flight type.
            if self.flights.domestic(i, True):  # Blue for domestic flights
                color = colors[0]
            elif self.flights.airline(i) == "KQ":  # Red for non-domestic KQ flights.
                color = colors[5]
            else:  # And the rest green
                color = colors[2]

            # If this is a park flight use the light color, otherwise dark.
            color = color[1] if solution.flight_type == ft.Park else color[0]

            # If it's part of a split flight, check whether the flight was repositioned.
            repositioned = False
            if solution.flight_type in [ft.Arr, ft.Park, ft.Dep]:
                j = i - [ft.Arr, ft.Park, ft.Dep].index(solution.flight_type)
                for k in range(2):
                    if self.solutions[j+k].bay_idx != self.solutions[j+k+1].bay_idx:
                        repositioned = True

            # If it was repositioned. Use a dotted line.
            linestyle = ":" if repositioned else "-"

            # Plot a line for the flight.
            eta = solution.eta
            etd = solution.etd
            plt.plot([eta, etd],
                     [solution.bay_idx] * 2, color=color, linewidth=4, linestyle=linestyle)

            if repositioned and solution.flight_type is ft.Arr:
                plt.text(eta, solution.bay_idx,  reposition_idx,
                         verticalalignment='center', horizontalalignment='right', )
                reposition_idx += 1

        # Configure plot's title, labels, legend, layout,  etc.
        plt.grid(True, color='0.85')
        plt.gcf().autofmt_xdate()
        plt.title(title, y=1.05)
        plt.xlabel("Time")
        plt.ylabel("Bay")
        domestic_patch = mpatches.Patch(color=colors[0][0], label='domestic')
        nondom_kq_patch = mpatches.Patch(color=colors[5][0], label='non-domestic KQ')
        nondom_oth_patch = mpatches.Patch(color=colors[2][0], label='non-domestic other')
        remote_line = mlines.Line2D([], [], color='black', linestyle=":", label='repositioned')
        plt.legend(handles=[domestic_patch,
                            nondom_kq_patch,
                            nondom_oth_patch,
                            remote_line],
                   bbox_to_anchor=(0., 1.0, 1., .10), loc=3,
                   ncol=4, mode="expand", borderaxespad=0.
                   )
        plt.tight_layout()

        return fig

    def create_gate_assignment_chart(self, title):
        # Create a new figure.
        fig = plt.figure(figsize=(8, 8))
        # Set the y-axis tick labels to gate names
        plt.yticks(range(self.airport.n_gates), self.airport.gate_names)

        # Set the axis limits
        plt.xlim([datetime.combine(self.flights.config['date'], time(0, 0, 0)),
                  datetime.combine(self.flights.config['date'], time(23, 59, 59))])
        plt.ylim([-1, self.airport.n_gates])


        # Format the x-axis so it displays the time of the day.
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())

        # For overlapping gate assignments move each flight to different levels on the plot.
        # Find pairs of conflicting flights on the same gate.
        gate_conflict_pairs = KeyPairDictionary()
        line_dy = {}
        for i in range(self.flights.n_flights):
            for j in range(i+1, self.flights.n_flights):
                if self.flights.time_conflict(i, j):
                    if self.solutions[i].gate_idx == self.solutions[j].gate_idx:
                        gate_conflict_pairs[i, j] = None

        # Loop through each solution
        for i, solution in enumerate(self.solutions):
            if solution.gate_idx is not None:
                # Allow 20 different levels for placing conflicting lines.
                dy_list = [False]*20
                # Loop through each flight the current flight has a conflict with.
                for pair in gate_conflict_pairs.pairs(i):
                    # If the flight has a level assigned to it. Mark that level as reserved.
                    if pair in line_dy:
                        dy_list[line_dy[pair]] = True

                # Look for a level that has not been reserved and reserve it for the current solution
                dy = 0
                while dy_list[dy]:
                    dy += 1
                line_dy[i] = dy

                # Calculate level position w.r.t. level 0.
                dy = (-1)**dy * ((dy+1) // 2)

                # Set the color based on flight type.
                if self.flights.domestic(i, True):  # Blue for domestic flights
                    color = colors[0][0]
                elif self.flights.airline(i) == "KQ":  # Red for non-domestic KQ flights.
                    color = colors[5][0]
                else:  # And the rest green
                    color = colors[2][0]

                # Use a dotted line if the flight is on a remote bay.
                linestyle = ":" if solution.bay_idx in self.airport.remote_bays else "-"

                eta = solution.eta
                etd = solution.etd
                plt.plot([eta, etd],
                         [solution.gate_idx - 0.2 * dy] * 2, linewidth=4, color=color, linestyle=linestyle)

        # Configure plot's title, labels, legend, layout,  etc.
        plt.grid(True, color='0.85')
        plt.gcf().autofmt_xdate()
        plt.title(title, y=1.05)
        plt.xlabel("Time")
        plt.ylabel("Gate")
        domestic_patch = mpatches.Patch(color=colors[0][0], label='domestic')
        nondom_kq_patch = mpatches.Patch(color=colors[5][0], label='non-domestic KQ')
        nondom_oth_patch = mpatches.Patch(color=colors[2][0], label='non-domestic other')
        remote_line = mlines.Line2D([], [], color='black', linestyle=":", label='on remote bay')
        plt.legend(handles=[domestic_patch,
                            nondom_kq_patch,
                            nondom_oth_patch,
                            remote_line],
                   bbox_to_anchor=(0., 1.0, 1., .10), loc=3,
                   ncol=4, mode="expand", borderaxespad=0.
                   )

        plt.tight_layout()
        return fig
