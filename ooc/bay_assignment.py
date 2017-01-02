from ooc import ft


class BayAssignment:
    """
    This class generated the lp code for the bay assignment problem.

    :param ooc.Flights flights: Flight object holding the information on all
       the flights of the day.

    :param bool compact: True to compact the generated lp code ad reduce
       the total number of lines.

    :param int line_width_limit: Suggested line width limit for the generated
       code. The code might exceed this limit since the check is done after
       new snippets have been added to the line, and for in some cases it's
       assumed that the line width will never reach the limit.
    """

    def __init__(self, flights, compact=True, line_width_limit=120, cplex=True):
        self.airport = flights.airport
        """"
        class:`ooc.Airport` object holding the information of
        the target airport.
        """

        self.flights = flights
        """
        class:`ooc.Flights` object holding the information of all
        flights of the day
        """

        self.compact = compact
        """
        True to compact the generated lp code and reduce the total number of lines.
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

        self.beta = self.flights.beta()
        """
        Weight for the airline preference objective function.
        """

        self.gamma = self.flights.gamma()
        """
        Weight for the penalties.
        """

        self.line_width_limit = line_width_limit
        """
        Line width limit of the generated code. Lines might exceed this limit
        by a bit, since the checks are done after the new snippet has been written.
        """

        # Originally lpsolve was being used to solve the problem. However as more constrains
        # where added it became unfeasible to solve the problem using lpsolve. So we switched
        # to cplex.
        # This flag was used in the transition period to allow both lpsolve and cplex code to be
        # generated. But since then the lpsolve generator is not supported anymore
        self.cplex = cplex
        """
        Flag indicating whether lpsolve or cplex code is to be generated. lpsolve is not
        supported anymore, so this flag should always be ``True``.
        """

    def save_lp_file(self, path):
        with open(path, "w") as f:
            f.write(self.lp_code())

    def lp_code(self):
        """
        :return: lp code for solving the bay assignment problem.
        """

        constraint_single_bay_compliance = self.constraint_single_bay_compliance()
        constraint_single_time_slot = self.constraint_single_time_slot()
        constraint_fueling = self.constraint_fueling()
        constraint_splitted_flight = self.constraint_splitted_flight()
        constraint_adjacency = self.constraint_adjacency()
        objective_function = self.objective_function()
        binary_decision_variables_declaration = self.binary_decision_variables_declaration()

        if self.cplex:
            code = "\n".join([
                objective_function,
                "\nSubject To\n",
                constraint_single_time_slot,
                constraint_single_bay_compliance,
                constraint_fueling,
                constraint_splitted_flight,
                constraint_adjacency,
                "\nBINARY\n",
                binary_decision_variables_declaration,
                "\nEND\n"
            ])

            # Since the code was originally created for lpsolve
            # we have to convert this lpsolve code to cplex code. This line should cover most of it.
            # There are more tweaks in this file.
            code = code.replace(";", "").replace(",", "").replace("//", "\\")
        else:
            raise Exception("The lpsolve generator is not supported anymore. Use the cplex generator instead.")
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

                # oOly add compliant flight bay combinations to the objective function.
                # This combination was never created and thus the decision variable
                # does not exist.
                if self.flights.bay_compliance(i, k):
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
                    z1 += " +{:<15.4f} {:10s}".format(constant, self.x(i, k))

                    # Add new line if necessary
                    if (not self.compact) or (len(z1.split("\n")[-1]) > self.line_width_limit):
                        z1 = z1.rstrip()
                        z1 += "\n    "

        return z1

    def of_max_airline_preference(self):
        """
        This objective function will add a term for each not-preferred bay assignment.

        :return: Objective function for maximizing airline bay preference.
        :rtype: string
        """
        # Initialize empty string that will hold the objective function.
        z2 = "// Maximization of airline preference\n    "

        # Loop through all flight that have a preference.
        for i in range(self.flights.n_flights):

            # Check whether a flight has some preference
            if self.flights.flight_schedule[i].preference is not None:
                # Add a term for each bay the flight has NO preference for.
                for k in range(self.airport.n_bays):
                    if k not in self.flights.flight_schedule[i].preference.bays:

                        # Only add terms for flight bay combinations that are valid.
                        if self.flights.bay_compliance(i, k):

                            # The constant will just be the objective function's weight factor.
                            constant = self.beta

                            # Generate string with the decision variable and it's constant
                            # and add it to the objective function.
                            z2 += " +{:<15.4f} {:10s}".format(constant, self.x(i, k))

                            # Add new line if necessary
                            if (not self.compact) or (len(z2.split("\n")[-1]) > self.line_width_limit):
                                z2 = z2.rstrip()
                                z2 += "\n    "
        return z2

    def penalty_values(self):
        """
        Add the penalty values to the objective function.

        :return: Objective function with the summation of all penalty values U, V, W and S.
        """

        of = "// Penalty values.\n   "
        for penalty_name in self.u_list + self.v_list + self.w_list+ self.s_list:
            # The constant will just be the objective function's weight factor.
            constant = self.gamma

            # Generate string with the penalty value and it's constant
            # and add it to the objective function.
            of += " +{:<15.4f} {:10s}".format(constant, penalty_name)

            # Add new line if necessary
            if (not self.compact) or (len(of.split("\n")[-1]) > self.line_width_limit):
                of = of.rstrip()
                of += "\n   "
        return of + "\n"

    def objective_function(self):
        """
        :return: The total bay assignment objective function.
        :rtype: string
        """
        # Create complete objective function by combining the three individual objective functions.
        return "Minimize\n{}\n\n{}\n{}\n".format(self.of_min_passenger_transport_distance(),
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

        if self.cplex:
            s = ""
        else:
            s = "// Binary decision variables declaration\nbinary\n   "
        for name in self.x_list:
            if self.cplex:
                s += " {:10s}".format(name)
            else:
                s += " {:10s},".format(name)
            # Add new line if necessary
            if len(s.split("\n")[-1]) > self.line_width_limit:
                s += "\n   "
        # Remove last comma and replace it by a semicolon to close the binary block.
        s = s[:-2] + ";\n\n"
        return s

    def x(self, i, k, allow_new=False):
        """
        Returns the name of the binary decision variable connecting a flight ``i``
        with bay ``k``.

        :param int i: Flight index
        :param int k: Bay index
        :param bool allow_new: If ``True`` it allows the creation of a
          new decision variable for new ``i`` and ``k`` combination.
        :return: The name of the binary decision variable
        """
        # Generate name.
        name = "X_{}_{}".format(i, k)

        # Add it to the decision variable name list if it's not in there already.
        if name not in self.x_list:
            if allow_new:
                self.x_list.append(name)
            else:
                raise Exception("Creating a new decision variable is not allowed.")

        return name

    def u(self, i, k):
        """
        :param i: Flight index
        :param k: Bay index
        :return: Name of the penalty value with the number of night towings.
        :rtype: string
        """
        name = "U_{}_{}".format(i, k)
        if name not in self.u_list:
            self.u_list.append(name)
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

    def s(self, i, j, k):
        """

        :param k: Bay index
        :param i: Flight 1 index
        :param j: Flight 2 index
        :return: Name of the adjacency soft constraint penalty value.
        """
        name = "S_{}_{}_{}".format(i, j, k)
        if name not in self.s_list:
            self.s_list.append(name)
        return name

    def constraint_single_bay_compliance(self):
        """
        These constraints make sure that a flight is only assigned to a
        single bay and that the flight is only assigned to compliant bays.

        :return: The bay compliance and single bay per aircraft constraints.
        :rtype: string
        """

        # This constraint is the only one allowed to create new X decision variables.
        # The reason behind this is to reduce the total number of decision variables.
        # There is no need to have decision variables for flight/bay combinations that
        # are not feasible.

        # Add a commend to the code to indicate where the constraints begin.
        c = "// Bay compliance and single bay per aircraft Constraint.\n"

        # Loop through each flight.
        for i in range(self.flights.n_flights):

            # Start writing the constraint for this flight.
            c += "bc_{}:\n".format(i)

            # Loop through each bay and check whether it's compliant with the aircraft used in the flight.
            for k in range(self.airport.n_bays):
                if self.flights.bay_compliance(i, k):

                    # If compliant add the term to the constraint's sum.
                    c += " + {:10s}".format(self.x(i, k, True))

                    # Add new line if necessary
                    if len(c.split("\n")[-1]) > self.line_width_limit:
                        c += "\n"

            # Finish the constraint, and loop back again fo the next flight.
            c += " = 1;\n"
        return c

    def constraint_single_time_slot(self):
        """
        These constraints make sure that only one flight is assigned to one bay at a time.

        :return: lp_code for the single time slot constraint.
        :rtype: string
        """

        # Add a commend to the code to indicate where the single time slot constrains begin.
        c = "// Single time slot constraints.\n"

        # i and j are flight indices.
        # Loop through all combinations of i and j.
        for i in range(self.flights.n_flights):

            # By starting index j at i + 1, we prevent adding the constraint for i == j and
            # prevent doubling the constrains. The constraint for (i, j) is the same a (j, i)
            for j in range(i + 1, self.flights.n_flights):

                # Only add the constraint if the two flights conflict
                if self.flights.time_conflict(i, j):

                    # Loop through all bays.
                    for k in range(self.airport.n_bays):

                        # Only add the constraint if both flights are compliant with the bay.
                        # If only one or none of them are compliant with the bay there will be
                        # no conflict on this particular bay thanks to the bay compliance constraint.
                        if self.flights.bay_compliance(i, k) and self.flights.bay_compliance(j, k):
                            c += "tc_{}_{}_{}: {:10s} + {:10s} <= 1;\n".format(i, j, k,
                                                                               self.x(i, k),
                                                                               self.x(j, k))
        c += "\n"
        return c

    def constraint_fueling(self):
        """
        These constraints make sure that departing aircraft are assigned to
        bays with fueling pits.

        :return: Fueling constraints.
        :rtype:
        """

        # These set of constraints are split in two. The first consists of all
        # non-domestic departing flights and "Full" domestic flights. The second
        # one are the long stay departing flights. This is done like this because
        # it's assumed that domestic flights can be fueled in the parking phase.

        c = "// Fueling constrains\n"

        # Loop through each flight.
        for i in range(self.flights.n_flights):
            # I'm way to tired right now to come up with names for these, so random letters.
            d = ""  # String holding the content of the constraint for this flight
            q = 0  # If 0, no constraint. If 1, departing non-domestic or full domestic. If 2, departing domestic.

            if (self.flights.departing(i) and not self.flights.domestic(i)) or \
               (self.flights.domestic(i) and (self.flights.flight_schedule[i].flight_type == ft.Full and
                                              (self.flights.departing(i)))):
                # Non-domestic departing flights and "Full" domestic flights.
                q = 1

                # Loop through each bay and add a term to the constraint's sum if it has a fueling port and
                # the flight and bay combination is compliant.
                for k in range(self.airport.n_bays):
                    if self.airport.fueling[k] and self.flights.bay_compliance(i, k):
                        d += " + {}".format(self.x(i, k))
                        # Add new line if necessary
                        if len(d.split("\n")[-1]) > self.line_width_limit:
                            d += "\n"

            elif self.flights.domestic(i) and (self.flights.departing(i)):
                # Long stay departing domestic flight. We don't need an explicit check
                # to check whether it's a long stay flight. Short stay flight where already handled by the
                # previous section.
                q = 2

                # Loop through each bay and add a term to the constraint for both the parking and
                # departing flights. Also checks whether the flight bay combination is compliant.
                for k in range(self.airport.n_bays):
                    if self.airport.fueling[k] and self.flights.bay_compliance(i, k):
                        d += " + {} + {}".format(self.x(i, k),
                                                 self.x(i - 1, k))
                        # Add new line if necessary
                        if len(d.split("\n")[-1]) > self.line_width_limit:
                            d += "\n"
            # Complete the constraint by adding the name and end.
            if q == 1:
                c += "fc_{}:\n{} = 1;\n".format(i, d)
            elif q == 2:
                c += "fc_{}:\n{} >= 1;\n".format(i, d)

        c += "\n"
        return c

    def constraint_splitted_flight(self):
        """
        These are soft constraints to limit the number of towings for splitted flights.
        For long stay overnight flights the aircraft is already placed at a bay, so

        :return: Splitted flight constraints.
        """

        c = "// Splitted constraints\n"

        # Loop through all flights.
        for i in range(self.flights.n_flights):

            # Check if this is a long stay flight.
            if self.flights.flight_schedule[i].flight_type == ft.Arr:

                # Check if this is an overnight flight
                if self.flights.is_overnight(i):

                    # Get current location. If the current location is unknown raise an error.
                    current_location = self.flights.flight_schedule[i].current
                    if current_location is None:
                        raise Exception("The current location of overnight, long stay flight '{}' is unknown.".
                                        format(self.flights.flight_schedule[i].in_flight_no))

                    # Get current bay
                    k_current = current_location.bay

                    # Set the night stay constraint on the arrival flight. This constraint indicates where the aircraft
                    # currently parked.
                    c += "nt_{}_{}: {} = 1; \n".format(i, k_current, self.x(i, k_current))

                    # Set the soft constraint between the arrival and parking flight. (i) → (i+1)
                    c += "sp_{}_{}: {} + {} = 1; \n".format(i, k_current,
                                                            self.x(i+1, k_current),
                                                            self.u(i, k_current))

                    # Set the soft constraint between the parking and departure flight. (i+1) → (i+2)
                    # The aircraft could have been moved  in the parking flight, so we have to create
                    # this constraint for all compliant bays.
                    for k in range(self.airport.n_bays):
                        if self.flights.bay_compliance(i, k):
                            c += "sp_{}_{}: {} - {} - {} + {} = 0; \n".format(i+1, k,
                                                                              self.x(i + 1, k),
                                                                              self.x(i + 2, k),
                                                                              self.u(i + 1, k),
                                                                              self.w(i + 1, k))
                else:
                    # This is not an overnight flight. So all three 'flights' have to be allocated.
                    # Loop through all compliant bays.
                    for k in range(self.airport.n_bays):
                        if self.flights.bay_compliance(i, k):
                            c += "sp_{}_{}: {} - {} - {} + {} = 0;\n".format(i, k,
                                                                             self.x(i, k), self.x(i + 1, k),
                                                                             self.v(i, k), self.w(i + 1, k))
                            c += "sp_{}_{}: {} - {} - {} + {} = 0;\n".format(i+1, k,
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

        # Loop through all combinations of flights
        for i in range(self.flights.n_flights):
            for j in range(i + 1, self.flights.n_flights):

                # Loop through each pair of bays with adjacency constrains.
                for bay_pair in self.airport.adjacency:
                    # Convert bay_pair from type tuple to list. This will give a copy we can modify.
                    bay_pair = list(bay_pair)

                    # Loop twice, so the constraints are created for flight/bay pairs (i/1, j/2) and (i/2 and j/1).
                    for _ in range(2):
                        # Unpack bay_pair list
                        bay_1, bay_2 = bay_pair

                        # Reverse the bay_pair list so that in the next iteration bay_1 and bay_2 are swapped.
                        bay_pair.reverse()

                        # Check if flights are compliant with the bays, if not, the constraint is not needed because
                        # the flight(s) won't be assigned to the bay anyways.
                        if self.flights.bay_compliance(i, bay_1) and self.flights.bay_compliance(j, bay_2):
                            # Create the constraint.
                            c += "ad_{}_{}_{}: {} + {} - {} <= 1;\n".format(bay_1, i, j,
                                                                            self.x(i, bay_1),
                                                                            self.x(j, bay_2),
                                                                            self.s(i, j, bay_1))

        c += "\n"
        return c
