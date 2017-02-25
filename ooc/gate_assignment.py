"""
The class in here generates the code for the bay assignment.
"""

from datetime import datetime, time
from math import isclose


class GateAssignment:
    """
    This class generated the lp code for the bay assignment problem.

    :param ooc.Airport airport: Airport object holding the information
    regarding the target airport.

    :param ooc.Flights: Flight object holding the information on all
        the flights of the day.
    """

    def __init__(self, flights, bays, line_width_limit=120):
        self.airport = flights.airport
        """"
        class:`ooc.Airport` object of holding the information of
        the target airport.
        """

        self.flights = flights
        """
        class:`ooc.Flights` object holding the information of all
        flights of the day
        """

        self.bay = bays
        """
        Array holding the bay for each flight.
        """

        self.x_list = []

        self.m_list = []

        self.line_width_limit = line_width_limit
        """
        Line width limit of the generated code. Lines might exceed this limit
        by a bit, since the checks are done after the new snippet has been written.
        """

        self.delta = 0.001
        self.epsilon = 1
        self.eta = 1

        self.terminal_a_gates = ['12', '13', '14', '15', '16', '17', '18', '19',
                                 '20', '21', '22', '23', '24', '20B']
        for i, gate_name in enumerate(self.terminal_a_gates):
            if gate_name in self.airport.gate_names:
                self.terminal_a_gates[i] = self.airport.gate_names.index(gate_name)

    def save_lp_file(self, path):
        with open(path, "w") as f:
            f.write(self.lp_code())

    def lp_code(self):
        print("Generating the lp code for the gate assignment...")

        of_min_bay_gate_distance = self.of_min_bay_gate_distance()
        of_airline_preference = self.of_airline_preference()
        constraint_single_gate_per_flight = self.constraint_single_gate_per_flight()
        constraint_time_conflict = self.constraint_time_conflict()
        # constraint_domestic = self.constraint_domestic()
        # constraint_kq_after_6pm = self.constraint_kq_after_6pm()
        binary_decision_variables_declaration = self.binary_decision_variables_declaration()
        of_penalty_variables = self.of_penalty_variables()

        lp_code_parts = [
            "Maximize",
            of_min_bay_gate_distance,
            of_airline_preference,
            of_penalty_variables,
            "Subject To",
            constraint_single_gate_per_flight,
            constraint_time_conflict,
            # constraint_domestic,
            # constraint_kq_after_6pm,
            "BINARY",
            binary_decision_variables_declaration,
            "END",
        ]

        return "\n\n".join(lp_code_parts)

    def departing_flights(self):
        """
        Generator yielding the flight index, assigned bay and flight object of departing flights.
        """
        for i in range(self.flights.n_flights):
            if self.flights.departing(i):
                yield i, self.bay[i], self.flights.flight_schedule[i]

    def x(self, i, l, allow_new=False):
        """
        Returns the name of the binary decision variable connecting a flight ``i``
        with bay ``k``.

        :param int i: Flight index
        :param int l: Gate index
        :param bool allow_new: If ``True`` it allows the creation of a
          new decision variable for new ``i`` and ``l`` combination.
        :return: The name of the binary decision variable
        """
        if not self.is_feasible(i, l):
            raise Exception("Unfeasible flight gate combination.")

        # Generate name.
        name = "X_{}_{}".format(i, l)

        # Add it to the decision variable name list if it's not in there already.
        if name not in self.x_list:
            if allow_new:
                self.x_list.append(name)
            else:
                raise Exception("Creating a new decision variable is not allowed.")
        return name

    def m(self, i, j, l):
        """
        Returns the name of the penalty value used in the .

        :param i: Flight 1 index
        :param j: Flight 2 index
        :param l: Gate index
        :returns: M penalty value name
        :rtype: String
        """
        name = "M_{}_{}_{}".format(i, j, l)
        if name not in self.m_list:
            self.m_list.append(name)
        return name

    def flight_located_at_gate(self, i, l):
        # Check if the flight is a remote and gate l is a dedicated bussing gate.
        if (self.bay[i] in self.airport.remote_bays) and (l in self.airport.bussing_gates):
            return True
        else:
            return isclose(self.airport.bay_gate_distance[self.bay[i]][l], 0.0)

    def has_preference(self, i, l):
        if self.flights.flight_schedule[i].preference is not None:
            return l in self.flights.flight_schedule[i].preference.gates
        else:
            return False

    def preference(self, i, l):
        # Check if this flight was placed on a bay connected to the gate
        if self.flight_located_at_gate(i, l):
            if self.has_preference(i, l):
                return 1
            else:
                return 0.8
        else:
            if self.has_preference(i, l):
                return 0.9
            return None

    def is_feasible(self, i, l):
        """
        Checks whether a certain flight gate combination is feasible.

        :param i: Flight index
        :param l: Gate index
        :return: True if flight gate combination is feasible.
        """
        # Get the bay assigned to the flight
        k = self.bay[i]
        if self.flights.domestic(i, departing=True):
            # If it's a domestic flight, then only the domestic gates are feasible. Also check if the bay gate
            # combination is feasible.
            return (l in self.airport.domestic_gates) and (self.airport.bay_gate_distance[k][l] is not None)
        else:
            # Domestic gates are unfeasible for non-domestic flights. Check bay gate combination as well.
            if (l not in self.airport.domestic_gates) and (self.airport.bay_gate_distance[k][l] is not None):
                # KQ flight after 6PM are only allowed in terminal A
                time_6pm = datetime.combine(self.flights.config['date'], time(hour=18))

                # Check if its a KQ flight after 6pm
                if (self.flights.flight_schedule[i].etd >= time_6pm) and (self.flights.airline(i) == "KQ"):
                    # If it is, check whether the gate is a terminal a gate.
                    return l in self.terminal_a_gates
                else:
                    # It's not, so it's feasible
                    return True
            else:
                return False

    def of_min_bay_gate_distance(self):
        print(" - Objective function: Minimization of bay gate distance")
        z6 = "\\ Minimization of bay gate distance.\n   "

        of_max_value = 0

        for i, k, flight in self.departing_flights():
            flight_max_value = 0
            for l in range(self.airport.n_gates):
                # Check if the bay gate combination is feasible
                if self.is_feasible(i, l):
                    bay_gate_distance = self.airport.bay_gate_distance[k][l]
                    constant = self.flights.n_passengers(i) \
                               * bay_gate_distance * self.delta
                    if constant > flight_max_value:
                        flight_max_value = constant

                    # Generate string with the decision variable and it's constant
                    # and add it to the objective function.
                    # Note that all of these factors are negative. This is because
                    # we want to minimize this objective function.
                    z6 += " -{:<17.4f} {:15s}".format(constant, self.x(i, l, True))

                    # Add new line if necessary
                    if len(z6.split("\n")[-1]) > self.line_width_limit:
                        z6 = z6.rstrip()
                        z6 += "\n   "
            of_max_value += flight_max_value

        self.epsilon = 2 * of_max_value
        return z6

    def of_airline_preference(self):
        print(" - Objective function: Maximization of airline preference.")
        z7 = "\\ Maximization of airline preference.\n   "

        max_value = 0

        for i, k, flight in self.departing_flights():
            for l in range(self.airport.n_gates):
                # Check if the bay gate combination is feasible
                if self.is_feasible(i, l):
                    preference = self.preference(i, l)
                    if preference is None:
                        continue
                    constant = self.epsilon * preference

                    max_value += constant

                    z7 += " +{:<17.4f} {:15s}".format(constant, self.x(i, l))

                    # Add new line if necessary
                    if len(z7.split("\n")[-1]) > self.line_width_limit:
                        z7 = z7.rstrip()
                        z7 += "\n   "

        self.eta = max_value if max_value >= self.epsilon else self.epsilon
        return z7

    def of_penalty_variables(self):
        print(" - Objective function: Penalty variables.")
        z8 = "\\ Penalty variables.\n   "

        for m in self.m_list:
            z8 += " -{:<20.4f}{:15s}".format(self.eta, m)
            # Add new line if necessary
            if len(z8.split("\n")[-1]) > self.line_width_limit:
                z8 = z8.rstrip()
                z8 += "\n   "

        return z8

    def binary_decision_variables_declaration(self):
        """
        :return: String containing the code to declare the binary decision variables as binary.
        :rtype: string
        """
        print(" - Binary decision variables declaration.")
        s = "\\ Binary decision variables\n   "
        for name in self.x_list + self.m_list:
            s += " {:15s}".format(name)

            # Add new line if necessary
            if len(s.split("\n")[-1]) > self.line_width_limit:
                s += "\n   "
        return s

    def constraint_single_gate_per_flight(self):
        """
        This constraint makes sure that one gate is assigned to each departing flight.
        """
        print(" - Constraint: Single gate per flight constraint.")
        c = "\\ Single gate per flight constraint.\n   "

        # Loop through each flight.
        for i, k, flight in self.departing_flights():
            # Start writing the constraint for this flight.
            c += "sg_{}:\n       ".format(i)

            # Loop through each bay and check whether it's compliant with the aircraft used in the flight.
            for l in range(self.airport.n_gates):
                # Check whether the bay gate combination is feasible.
                if self.is_feasible(i, l):

                    # If compliant add the term to the constraint's sum.
                    c += " + {:10s}".format(self.x(i, l))

                    # Add new line if necessary
                    if len(c.split("\n")[-1]) > self.line_width_limit:
                        c += "\n       "

            # Finish the constraint, and loop back again fo the next flight.
            c += " = 1\n   "
        return c

    def constraint_time_conflict(self):
        """

        :return:
        """
        print(" - Constraint: Time conflict.")
        c = "\\ Time conflict constrains\n"

        # Loop through all pairs of flights
        for i, k, flight in self.departing_flights():
            for j, j_k, j_flight in self.departing_flights():
                # The time conflict constraint for pairs (i, j) and (j, i) are the same. So we can half the number of
                # constraints by only creating then for one of these pairs.
                if i < j:
                    # Check whether there is a time conflict.
                    if self.flights.time_conflict(i, j):
                        # Loop through each gate and check whether the bay gate combinations are feasible.
                        for l in range(self.airport.n_gates):
                            if (self.is_feasible(i, l)) and \
                               (self.is_feasible(j, l)):
                                c += "   tc_{}_{}_{}: {} + {} - {} <= 1\n".format(i, j, l,
                                                                                  self.x(i, l),
                                                                                  self.x(j, l),
                                                                                  self.m(i, j, l))
        return c

    # These constraints where removed from the LP file since they are not neccesary anymore.
    # The is_feasible function takes the domestic and after 6pm constraints into account
    # so the decision variables for cases which these constraints would have rejected are
    # never created. Thus adding these constraints would be redundant.

    # def constraint_domestic(self):
    #     print(" - Constraint: Domestic flight.")
    #
    #     c = "\\ Domestic flight constraints\n   "
    #
    #     # Loop through all departing flights
    #     for i, k, flight in self.departing_flights():
    #         # if self.flights.domestic(i, force_departing=True):
    #         #     continue
    #         # Start with the constraint for flight i.
    #         c += "do_{}:\n       ".format(i)
    #
    #         # Loop through all domestic gates.
    #         for l in self.airport.domestic_gates:
    #             # Check if bay gate combination is feasible.
    #             if self.is_feasible(i, l):
    #                 c += " +{:10s}".format(self.x(i, l))
    #
    #                 # Add new line if necessary
    #                 if len(c.split("\n")[-1]) > self.line_width_limit:
    #                     c = c.rstrip()
    #                     c += "\n       "
    #
    #         # Finish constraint by adding either equality to one or zero depending on whether this is a domestic
    #         # flight or not.
    #         if self.flights.domestic(i, departing=True):
    #             c += " = 1\n   "
    #         else:
    #             c += " = 0\n   "
    #
    #     return c

    # def constraint_kq_after_6pm(self):
    #     print(" - Constraint: KQ flights after 6pm.")
    #     c = "\\ Constraints for KQ flights after 6pm\n   "
    #     time_6pm = datetime.combine(self.flights.config['date'], time(hour=18))
    #
    #     non_kq_gates = ['4', '5', '7', '8', '9', '10']
    #     for i, gate_name in enumerate(non_kq_gates):
    #         if gate_name in self.airport.gate_names:
    #             non_kq_gates[i] = self.airport.gate_names.index(gate_name)
    #
    #     for i, k, flight in self.departing_flights():
    #         if (flight.etd >= time_6pm) and (self.flights.airline(i) == "KQ"):
    #             c += "k6_{}:\n       ".format(i)
    #             for l in non_kq_gates:
    #                 if self.is_feasible(i, l):
    #                     c += " +{:10s}".format(self.x(i, l))  # Pycharm might complain here. It's fine.
    #
    #                     # Add new line if necessary
    #                     if len(c.split("\n")[-1]) > self.line_width_limit:
    #                         c = c.rstrip()
    #                         c += "\n       "
    #
    #             # Finish constraint.
    #             c += " = 0\n   "
    #
    #     return c

