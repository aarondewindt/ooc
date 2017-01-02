

class BayAssignmentSolution:
    """
    :param ooc.BayGateSolver bay_gate_solver:
    """

    def __init__(self, bay_gate_solver):
        self.airport = bay_gate_solver.airport
        """"
        class:`ooc.Airport` object of holding the information of
        the target airport.
        """

        self.flights = bay_gate_solver.flights
        """
        class:`ooc.Flights` object holding the information of all
        flights of the day
        """

        self.bay_assignment = bay_gate_solver.bay_assignment
        """
        class:`ooc.BayAssignment` object used to generate the bay assignment lp code.
        """

        self.jid = bay_gate_solver.jid
        """
        Job id. This is a unique id for a specific run or set of runs. The workspace
        folder will be named after the jid.
        """

        self.workspace_path = bay_gate_solver.workspace_path
        """
        Path to directory which will hold all of the generated lp files ond solutions.
        """

        self.bay_sol_path = bay_gate_solver.bay_sol_path
        """
        Path to the cplex solution file.
        """

    def load_solution(self):
        pass


