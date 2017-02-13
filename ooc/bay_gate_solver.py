from os import mkdir, remove, system
from os.path import isdir, isfile, abspath, normpath, join
import subprocess
import sys
import xml.etree.ElementTree as ET  #: the extra-terrestrial
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta, datetime, time

from ooc import print_color

from ooc import Airport, Flights, BayAssignment, FlightSolution, GateAssignment, ft
from ooc.key_pair_dictionary import KeyPairDictionary


class BayGateSolver:
    """
    This class is used to generate and solve the bay gate assignment
    problem.

    :param string airport_path: Path to directory holding the airport data

    :param string flights_path: Path to directory holding the flights data.
    """

    def __init__(self, airport_data_path, flights_data_path, jid, cplex_command="cplex"):
        self.airport = Airport(airport_data_path=airport_data_path)
        """"
        class:`ooc.Airport` object of holding the information of
        the target airport.
        """

        self.flights = Flights(flight_data_path=flights_data_path, airport=self.airport)
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

        # Check whether we can access cplex from the command line.
        try:
            subprocess.run([cplex_command + " -c help"], shell=True, stdout=subprocess.PIPE)
            # We can. Store command for later use.
            self.cplex_command = cplex_command
        except OSError:
            # We can't. We'll have to run the solver manually.
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
                f.write("""*""")

    def init_solution_list(self):
        """
        Initializes the list that will hold the solution eventually.
        """
        for i, flight in enumerate(self.flights.flight_schedule):
            solution = FlightSolution(i)
            self.solutions.append(solution)

            solution.flight_type = flight.flight_type
            solution.in_flight_no = flight.in_flight_no
            solution.origin = flight.origin
            solution.eta = flight.eta  #
            solution.reg_no = flight.reg_no
            solution.out_flight_no = flight.out_flight_no
            solution.dest = flight.dest
            solution.etd = flight.etd
            solution.ac_type = flight.ac_type

    def solve_bay_assignment(self):
        """
        Generates the lp code needed to solve the bay assignment,
        solves it using cplex and loads in the solution.
        """
        bay_assignment = BayAssignment(self.flights)

        # Generate and save lp code.
        with open(self.bay_lp_path, "w") as f:
            f.write(bay_assignment.lp_code())

        if self.cplex_command is not None:
            print("Solving bay assignment with cplex...")
            # Remove old solution file
            if isfile(self.bay_sol_path):
                remove(self.bay_sol_path)

            # Try to solve it.
            result = subprocess.run([self.cplex_command + " -c 'read {}' optimize 'write {}'".format(
                self.bay_lp_path, self.bay_sol_path
            )], shell=True, stdout=subprocess.PIPE)

            if isfile(self.bay_sol_path):
                print_color.pr_lg(result.stdout.decode("utf-8"))
            else:
                print(result.stdout.decode("utf-8"))
                raise Exception("No solution file was generated for the bay assignment.")

            print("Bay assignment solved\n")
        else:
            print("Cplex is not available in the command line.\n"
                  "The bay assignment lp code was generated and saved at\n{}\n".format(self.bay_lp_path) +
                  "Please solve it in cplex and save the resulting .sol (xml) file at\n{}\n".format(self.bay_sol_path))

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
                assigned = bool(int(element.get("value")))  # If True, than flight i has been assigned to bay k.
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
        bays = [solution.bay_idx for solution in self.solutions]
        if bays[0] is None:
            raise Exception("No bay assignment solutions has been loaded.")

        gate_assignment = GateAssignment(self.flights, bays)

        # Generate and save lp code.
        with open(self.gate_lp_path, "w") as f:
            f.write(gate_assignment.lp_code())

        if self.cplex_command is not None:
            print("Solving gate assignment with cplex...")
            # Remove old solution file
            if isfile(self.gate_sol_path):
                remove(self.gate_sol_path)

            # Try to solve it.
            result = subprocess.run([self.cplex_command + " -c 'read {}' optimize 'write {}'".format(
                self.gate_lp_path, self.gate_sol_path
            )], shell=True, stdout = subprocess.PIPE)

            if isfile(self.gate_sol_path):
                print_color.pr_lg(result.stdout.decode("utf-8"))
            else:
                sys.stderr.write(result.stdout.decode("utf-8"))
                raise Exception("No solution file was generated for the gate assignment.")

            print("Gate assignment solved\n")
        else:
            print("Cplex is not available in the command line.\n"
                  "The gate assignment lp code was generated and saved at\n{}\n".format(self.gate_lp_path) +
                  "Please solve it in cplex and save the resulting .sol (xml) file at\n{}\n".format(self.gate_sol_path))

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
                assigned = bool(int(element.get("value")))  # If True, than flight i has been assigned to bay k.
                if assigned:
                    # Sanity check.
                    if self.solutions[i].gate_idx is None:
                        self.solutions[i].gate_idx = l
                        self.solutions[i].gate = self.airport.gate_names[l]
                    else:
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

        s = self.solutions[0].str_heading()
        for solution in self.solutions:
            s += solution.str_data()

        print(s)

    def create_bay_assignment_chart(self):
        fig = plt.figure()
        plt.yticks(range(self.airport.n_bays), self.airport.bay_names)
        plt.xlim([datetime.combine(self.flights.config['date'], time(0, 0, 0)),
                  datetime.combine(self.flights.config['date'], time(23, 59, 59))])

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())

        last_color = 1

        for i, solution in enumerate(self.solutions):
            if solution.flight_type is ft.Arr:
                last_color = (last_color + 1) % 9 + 1
                color = last_color
            elif solution.flight_type is ft.Full:
                color = 0
            eta = datetime.combine(self.flights.config['date'], solution.eta)
            etd = datetime.combine(self.flights.config['date'], solution.etd)
            if eta > etd:
                plt.plot([eta, etd + timedelta(days=1)],
                         [solution.bay_idx] * 2,
                         [eta - timedelta(days=1), etd],
                         [solution.bay_idx] * 2
                         , color="C{}".format(color))
            else:
                plt.plot([eta, etd],
                         [solution.bay_idx] * 2, color="C{}".format(color))

        plt.gcf().autofmt_xdate()
        return fig

    def create_gate_assignment_chart(self):
        fig = plt.figure()
        plt.yticks(range(self.airport.n_gates), self.airport.gate_names)
        plt.xlim([datetime.combine(self.flights.config['date'], time(0, 0, 0)),
                  datetime.combine(self.flights.config['date'], time(23, 59, 59))])

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())

        gate_conflict_pairs = KeyPairDictionary()
        line_dy = {}

        for i in range(self.flights.n_flights):
            for j in range(i+1, self.flights.n_flights):
                if self.flights.time_conflict(i, j):
                    if self.solutions[i].gate_idx == self.solutions[j].gate_idx:
                        gate_conflict_pairs[i, j] = None

        for i, solution in enumerate(self.solutions):
            if solution.gate_idx is not None:
                # Allow 20 different levels for placing conflicting lines.
                dy_list = [False]*20
                for pair in gate_conflict_pairs.pairs(i):
                    if pair in line_dy:
                        dy_list[line_dy[pair]] = True
                dy = 0
                while dy_list[dy]:
                    dy += 1
                line_dy[i] = dy

                eta = datetime.combine(self.flights.config['date'], solution.eta)
                etd = datetime.combine(self.flights.config['date'], solution.etd)
                plt.plot([eta, etd],
                         [solution.gate_idx - 0.2*dy] * 2)

        plt.gcf().autofmt_xdate()
        return fig



