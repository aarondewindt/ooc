from os import mkdir, remove, system
from os.path import isdir, isfile, abspath, normpath, join
import subprocess
import sys


from ooc import Airport, Flights, BayAssignment


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

        self.bay_assignment = BayAssignment(self.flights)
        """
        class:`ooc.BayAssignment` object used to generate the bay assignment lp code.
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

        # Create the directory if it doesn't exist yet.
        if not isdir(self.workspace_path):
            mkdir(self.workspace_path)

        # Create a few path to relevant paths.
        self.bay_lp_path = normpath(join(self.workspace_path, "bay.lp"))
        self.bay_sol_path = normpath(join(self.workspace_path, "bay.sol"))
        self.gate_lp_path = normpath(join(self.workspace_path, "gate.lp"))
        self.gate_sol_path = normpath(join(self.workspace_path, "gate.sol"))

        # Check whether we can access cplex from the command line.
        try:
            # We can. Store command for later use.
            subprocess.run([cplex_command + " -c help"], shell=True, stdout=subprocess.PIPE)
            self.cplex_command = cplex_command
        except OSError:
            # We can't. We'll have to run the solver manually.
            self.cplex_command = None

    def solve_bay_assignment(self):
        """
        Generates the lp code needed to solve the bay assignment,
        solves it using cplex and loads in solution.
        """

        # Generate and save lp code.
        with open(self.bay_lp_path, "w") as f:
            f.write(self.bay_assignment.lp_code())

        if self.cplex_command is not None:
            print("solving bay assignment with cplex...")
            # Remove old solution file
            if isfile(self.bay_sol_path):
                remove(self.bay_sol_path)

            # Try to solve it.

            # We can. Store command for later use.
            subprocess.run([self.cplex_command + " -c 'read {}' optimize 'write {}'".format(
                self.bay_lp_path, self.bay_sol_path
            )], shell=True)

            if not isfile(self.bay_sol_path):
                raise Exception("No solution file was generated for the bay assignment.")

            print("solve solving bay assignment")
        else:
            print("Cplex is not available in the command line.\n"
                  "The bay assignment lp code was generated and saved at\n{}\n".format(self.bay_lp_path) +
                  "Please solve it in cplex and save the resulting .sol file at\n{}\n".format(self.bay_sol_path))

    def load_bay_assignment_solution(self):
        pass



