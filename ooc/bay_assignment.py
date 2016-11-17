from ooc import ft

# z1 bay objective function containing the passenger transport distance
# z2 bay objective function containing the flight preferences
# z3 bay objective function containing the penalty values for repositioning
# z4 total bay objective function excluding penalty values
# z5 total bay objective function including penalty values


class BayAssignment:
    """
    This class generated the lp code for the bay assignment problem.

    :param ooc.Flights flights: Flight object holding the information on all
       the flights of the day.
    :param bool compact: True to compact the generated lp code ad reduce
       the total number of lines.
    """

    def __init__(self, flights, compact=True, line_width_limit=120):
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

        self.compact = compact
        """
        True to compact the generated lp code ad reduce the total number of lines.
        """

        self.x_list = []
        """
        List holding the names of all the binary decision variables
        connecting flights with bays.
        """

        self.u_list = []
        """
        List holding the names of the penalty values containing the number
        of towings from arrival to parking in the night shift.
        """

        self.v_list = []
        """
        List holding the names of the penalty values with the number of
        towings from parking to departure.
        """

        self.w_list = []
        """
        List holding the names of the penalty values containing the number
        of towings during day time.
        """

        self.s_list = []
        """
        List holding the names of the adjacency constraint penalty values
        """

        self.alpha = 1
        """
        Weight for the passenger transport distance objective function.
        """

        self.beta = 1
        """
        Weight for the airline preference objective function.
        """

        self.gamma = 1
        """
        Weight for the penalties.
        """

        self.line_width_limit = line_width_limit
        """
        Line width limit of generated code. Lines might exceed this limit
        by a bit, since the checks are done after the new snippet have
        been written.
        """

    def lp_code(self):
        """
        :return: lp solve code for solving the bay assignment problem
        """

        code = "{}\n{}\n".format(self.objective_function(),
                                 self.binary_decision_variables_declaration())

        return code

    def of_min_passenger_transport_distance(self):
        """
        :return: Objective function for minimizing passenger transport
           between the check-in terminal and bay. aka z1.
        :rtype: string
        """
        # Initialize string that will hold the object function
        z1 = "// Minimization of passenger transport distance\n    "

        # Loop through all flight and bay combinations.
        for i in range(self.flights.n_flights):
            for k in range(self.airport.n_bays):
                # Calculate the constant for this decision variable.
                # This constant is the number of passengers in the flight
                # multiplied by the distance between the flight and terminal
                # multiplied by this objective function's weight `alpha`.
                constant = self.flights.n_passengers(i) \
                         * self.airport.terminal_bay_distance(self.flights.terminal(i),
                                                              k) \
                         * self.alpha

                # Generate string with the decision variable and it's constant
                # and add it to the objective function.
                # Note that all of these factors are negative. This is because
                # we want to minimize this objective function.
                z1 += " -{:15.4f} {:10s}".format(constant, self.x(i, k))

                # Add new line if necessary
                if (not self.compact) or (len(z1.split("\n")[-1]) > self.line_width_limit):
                    z1 = z1.rstrip()
                    z1 += "\n    "

        return z1

    def of_max_airline_preference(self):
        """
        :return: Objective function for maximizing airline bay preference.
        :rtype: string
        """
        # Initialize empty string that will hold the objective function.
        z2 = "// Maximization of airline preference\n    "

        # Loop through all flight and bay combinations.
        for i in range(self.flights.n_flights):
            for k in range(self.airport.n_bays):
                # Calculate the constant for this decision variable.
                # This constant is the flight-bay preference multiplied
                # by this objective function's weight `beta`.
                constant = self.flights.preference(i, k) \
                           * self.beta

                # Generate string with the decision variable and it's constant
                # and add it to the objective function.
                z2 += " +{:15.4f} {:10s}".format(constant, self.x(i, k))

                # Add new line if necessary
                if (not self.compact) or (len(z2.split("\n")[-1]) > self.line_width_limit):
                    z2 = z2.rstrip()
                    z2 += "\n    "

        return z2

    def penalty_values(self):
        """
        :return: Objective function with the summation of all penalty values U, V, W.
        """
        return "// Penalty values\n" \
               "    +{constant:10.4f} U \n" \
               "    +{constant:10.4f} V \n" \
               "    +{constant:10.4f} W \n".format(constant=self.gamma)

    def objective_function(self):
        """
        :return: The total bay assignment objective function.
        :rtype: string
        """
        # Create total objective function by concatenating the individual objective
        # objective functions with newlines in between and adding `max:` and `;` to
        # the front and back.
        return "max:\n{}\n\n{}\n{};\n".format(self.of_min_passenger_transport_distance(),
                                              self.of_max_airline_preference(),
                                              self.penalty_values())

    def binary_decision_variables_declaration(self):
        """
        :return: String containing the code to declare the binary decision variables as binary.
        :rtype: string
        """
        if len(self.x_list) == 0:
            # If there are no variables in the list generate the objective function to generate them.
            self.objective_function()

        s = "// Binary decision variables declaration\nbinary\n   "
        for name in self.x_list:
            s += " {:10s},".format(name)
            # Add new line if necessary
            if len(s.split("\n")[-1]) > self.line_width_limit:
                s += "\n   "
        # Remove last comma and replace it by a semicolon to close the binary block.
        s = s[:-2] + ";"
        return s

    def x(self, i, k):
        """
        Returns the name of the binary decision variable connecting a flight ``i``
        with bay ``k``.

        :param int i: Flight index
        :param int k: Bay index
        :return: The name of the binary decision variable
        """
        # Generate name.
        name = "X_{}_{}".format(i, k)

        # Add it to the decision variable name list if it's not in there already.
        if name not in self.x_list:
            self.x_list.append(name)

        return name

    def v(self, i, k):
        """
        :param i: Flight index
        :param k: Bay index
        :return: Name of the penalty value with the number of towings from parking to departure.
        :rtype: string
        """
        name = "V_{}_{}".format(i, k)
        if name not in self.v_list:
            self.v_list.append(name)
        return name

    def w(self, i, k):
        """
        :param i: Flight index
        :param k: Bay index
        :return: Name of the penalty value with the number of towings during day time.
        """
        name = "W_{}_{}".format(i, k)
        if name not in self.w_list:
            self.w_list.append(name)
        return name

    def s(self, k, i, j):
        """

        :param k: Bay index
        :param i: Flight 1 index
        :param j: Flight 2 index
        :return: Name of the adjacency soft constraint penalty value.
        """
        name = "S_{}_{}".format(i, k)
        if name not in self.s_list:
            self.s_list.append(name)
        return name

    def constraint_single_time_slot(self):
        """
        These constraints make sure that only one flight is assigned to one bay at a time.

        :return: lp_code for the single time slot constraint.
        :rtype: string
        """
        c = "// Single time slot constraints.\n"

        for i in range(self.flights.n_flights):
            for j in range(self.flights.n_flights):
                for k in range(self.airport.n_bays):
                    if i != j and self.flights.time_conflict(i, j):
                        c += "tc_{}_{}: {:10s} + {:10s} <= 1;\n".format(i, j,
                                                                        self.x(i, k),
                                                                        self.x(j, k))
        c += "\n"
        return c

    def constraint_single_bay_compliance(self):
        """
        These constraints make sure that a flight is only assigned to a bay
        if it's aircraft fits in the bay and that only one bay is assigned
        per flight.
        :return: The bay compliance and single bay per aircraft constraints.
        :rtype: string
        """

        c = "// Bay compliance and single bay per aircraft Constraint.\n"

        for i in range(self.flights.n_flights):
            c += "bc_{}:".format(i)
            for k in range(self.airport.n_bays):
                if self.flights.bay_compliance(i, k):
                    c += " + {:10s}".format(self.x(i, k))
                    # Add new line if necessary
                    if len(c.split("\n")[-1]) > self.line_width_limit:
                        c += "\n"
            c += " = 1;\n"
        return c

    def constraint_fueling(self):
        """
        These constraints make sure that departing aircrafts are assingned to
        bay with fueling pits.
        :return: Fueling constraints.
        :rtype:
        """

        # These set of constraints are split in two. The first consists of all
        # non-domestic departing flights and "Full" domestic flights. The second
        # one are the long stay departing flights. This is done like this because
        # it's assumed that domestic flights can be fueled in the parking phase.

        c = "// Fueling constrains"

        for i in range(self.flights.n_flights):
            # I'm way to tired right now to come up with names for these, so random letters.
            d = ""  # Holds the content of the the constraint for this flight
            q = 0  # If 0, no constraint. If 1, dep non-domestic or full domestic. If 2, dep domestic.

            if (not self.flights.domestic(i) and (self.flights.flight_schedule[i].flight_type in [ft.Full, ft.Dep]))or \
               (self.flights.domestic(i) and (self.flights.flight_schedule[i].flight_type == ft.Full)):
                # Non-domestic departing flights and "Full" domestic flights.
                q = 1
                for k in range(self.airport.n_bays):
                    if self.airport.fueling[k]:
                        d += " + {}".format(self.x(i, k))
                        # Add new line if necessary
                        if len(d.split("\n")[-1]) > self.line_width_limit:
                            d += "\n"
            elif self.flights.domestic(i) and (self.flights.flight_schedule[i].flight_type == ft.Dep):
                # Long stay departing domestic flight.
                q = 2
                for k in range(self.airport.n_bays):
                    if self.airport.fueling[k]:
                        d += " + {} + {}".format(self.x(i, k),
                                                 self.x(j, k))
                        # Add new line if necessary
                        if len(d.split("\n")[-1]) > self.line_width_limit:
                            d += "\n"
            if q == 1:
                c += "fc_{}: {} = 1;".format(i, d)
            elif q == 2:
                c += "fc_{}: {} >= 1;".format(i, d)
        c += "\n"
        return c

    def constraint_splitted_flight(self):
        """
        These are soft constraints to limit the number of towings for splitted flights.
        :return: Splitted flight constraints.
        """

        c = "// Splitted constraints\n    "

        for i in range(self.flights.n_flights):
            if self.flights.flight_schedule[i].flight_type == ft.Arr:
                for k in range(self.airport.n_bays):
                    c += "sp_{}_{}: {} - {} - {} + {} = 0;\n".format(i, k,
                                                                     self.x(i, k), self.x(i + 1, k),
                                                                     self.v(i, k), self.w(i + 1, k))
                    c += "sp_{}_{}: {} - {} - {} + {} = 0;\n".format(i, k,
                                                                     self.x(i + 1, k), self.x(i + 2, k),
                                                                     self.v(i + 1, k), self.w(i + 2, k))
        c += "\n"
        return c

    def constraint_adjacency(self):
        """
        This is a soft constraint to optimize gate usage. Bays 10 and 11 can only
        be loaded from gate 10 and bays 5 and 6 from gate 5. Because of this we want
        it is only possible to board bays 10/11, 5/6 one at a time from the gate, so
        the second flight would have to be bussed.
        This constraint prevents two departing time conflicting flights to be placed
        adjacent to each on these bays. However it's not a hard constraint, since a
        hard constraint would move the conflicting flight to a remote bay, which would
        be worse.

        :return: Adjacency constrains
        """
        c = "// Adjacency constraint\n"

        # Loop through each pair of bays with adjacency constrains.
        for bay_1, bay_2 in self.flights.adjacency:
            # Loop through all combinations of flights.
            for i, flight_1 in enumerate(self.flights.flight_schedule):
                for j, flight_2 in enumerate(self.flights.flight_schedule):
                    if i != j:
                        # Only create the constraint for departing time conflicting flights.
                        if (flight_1.flight_type == ft.Dep) and (flight_2.flight_type == ft.Dep):
                            if self.flights.time_conflict(i, j):
                                c += "ad_{}_{}_{}: {} + {} - {} <= 1;\n".format(bay_1, i, j,
                                                                                self.x(i, bay_1),
                                                                                self.x(j, bay_2),
                                                                                self.s(bay_1, i, j))
        c += "\n"
        return c
