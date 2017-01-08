from datetime import time


class GateAssignment:
    """
    This class generated the lp code for the bay assignment problem.

    :param ooc.Airport airport: Airport object holding the information
    regarding the target airport.

    :param ooc.Flights: Flight object holding the information on all
        the flights of the day.
    """

    def __init__(self, flights, bay, line_width_limit=120):
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

        self.bay = bay
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

        self.epsilon = 1
        self.eta = 1

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
        # Generate name.
        name = "X_{}_{}".format(i, l)

        # Add it to the decision variable name list if it's not in there already.
        if name not in self.x_list:
            if allow_new:
                self.x_list.append(name)
            else:
                raise Exception("Creating a new decision variable is not allowed.")
        return name

    def m(self, i, l):
        """
        Returns the name of the penalty value used in the max two flights per gate constraint.

        :param i: Flight 1 index
        :param l: Gate index
        :returns: M penalty value name
        :rtype: String
        """
        name = "M_{}_{}".format(i, l)
        if name not in self.m_list:
            self.m_list.append(name)
        return name

    def preference(self, i, l):
        if self.flights.flight_schedule[i].preference is not None:
            return 1 if l in self.flights.flight_schedule[i].preference.gates else None
        else:
            return None

    def of_min_bay_gate_distance(self):
        z6 = "\\ Minimization of bay gate distance.\n    "

        max_value = 0

        for i, k, flight in self.departing_flights():
            for l in range(self.airport.n_gates):
                bay_gate_distance = self.airport.bay_gate_distance[k][l]
                # If the bay gate distance is None if it was marked as infeasible. So only
                # create/add the decision variable for the bay gate combination if it's
                # feasible.
                if bay_gate_distance is not None:
                    constant = self.flights.n_passengers(i) \
                               * bay_gate_distance
                    max_value += constant

                    # Generate string with the decision variable and it's constant
                    # and add it to the objective function.
                    # Note that all of these factors are negative. This is because
                    # we want to minimize this objective function.
                    z6 += " -{:<15.4f} {:10s}".format(constant, self.x(i, l, True))

                    # Add new line if necessary
                    if len(z6.split("\n")[-1]) > self.line_width_limit:
                        z6 = z6.rstrip()
                        z6 += "\n    "

        return z6

    def of_airline_preference(self):
        z7 = "\\ Maximization of airline preference.\n    "

        max_value = 0

        for i, k, flight in self.departing_flights():
            for l in range(self.airport.n_gates):
                bay_gate_distance = self.airport.bay_gate_distance[k][l]
                # Check if the bay gate combination is feasible
                if bay_gate_distance is not None:
                    preference = self.preference(i, l)
                    if preference is None:
                        continue
                    constant = self.epsilon * preference

                    max_value += constant

                    z7 += " -{:<15.4f} {:10s}".format(constant, self.x(i, l))

                    # Add new line if necessary
                    if len(z7.split("\n")[-1]) > self.line_width_limit:
                        z7 = z7.rstrip()
                        z7 += "\n    "

        return z7

    def of_penalty_variables(self):
        z8 = "\\ Penalty variables.\n   "

        for m in self.m_list:
            z8 += " +{:10s}".format(m)
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
        s = "\\ Binary decision variables\n   "

        for name in self.x_list:
            s += " {:10s}".format(name)

            # Add new line if necessary
            if len(s.split("\n")[-1]) > self.line_width_limit:
                s += "\n   "
        return s

    def constraint_single_gate_to_flight(self):
        """
        This constraint makes sure that one gate is assigned to each departing flight.
        """

        c = "\\ Single gate to flight constraint.\n"

        # Loop through each flight.
        for i, k, flight in self.departing_flights():
            # Start writing the constraint for this flight.
            c += "sg_{}:\n".format(i)

            # Loop through each bay and check whether it's compliant with the aircraft used in the flight.
            for l in range(self.airport.n_gates):
                # Check whether the bay gate combination is feasible.
                if self.airport.bay_gate_distance[k][l] is not None:

                    # If compliant add the term to the constraint's sum.
                    c += " + {:10s}".format(self.x(i, l))

                    # Add new line if necessary
                    if len(c.split("\n")[-1]) > self.line_width_limit:
                        c += "\n"

            # Finish the constraint, and loop back again fo the next flight.
            c += " = 1\n"
        return c

    def constraint_max_two_flights_per_gate(self):
        """

        :return:
        """

        c = "\\ Max two flights per gate constrains\n"

        # Create a constraint for each departing flight.
        for i, k, flight in self.departing_flights():
            # Loop through each gate.
            for l in range(self.airport.n_gates):
                # Check if bay gate combination is feasible.
                if self.airport.bay_gate_distance[k][l] is not None:
                    # Create the constraint for flight i gate l combination
                    d = "mg_{}_{}:\n".format(i, l)

                    # Number of terms being added to the constraint. If there are less than two, than the
                    # constraint is unnecessary.
                    n_terms = 0

                    # Add a term for each flight that has a time conflict with flight i and is feasible to connect to
                    # gate l.
                    for j, j_k, j_flight in self.departing_flights():
                        if self.flights.time_conflict(i, j) and (self.airport.bay_gate_distance[j_k][l] is not None):
                            n_terms += 1
                            d += " +{:10s}".format(self.x(j, l))
                        # Add new line if necessary
                        if len(d.split("\n")[-1]) > self.line_width_limit:
                            d = d.rstrip()
                            d += "\n"

                    # Finish the constraint ony if at least two terms where added to it.
                    if n_terms >= 2:
                        # Add the penalty variable and finish the constraint.
                        c += d + "-{} <= 1\n".format(self.m(i, l))

        return c

    def constraint_domestic(self):
        c = "\\ Domestic flight constraints\n"

        # Loop through all departing flights
        for i, k, flight in self.departing_flights():
            # Start with the constraint for flight i.
            c += "do_{}:\n".format(i)

            # Loop through all domestic gates.
            for l in self.airport.domestic_gates:
                # Check if bay gate combination is feasible.
                if self.airport.bay_gate_distance[k][l] is not None:
                    c += " +{:10s}".format(self.x(i, l))

                    # Add new line if necessary
                    if len(c.split("\n")[-1]) > self.line_width_limit:
                        c = c.rstrip()
                        c += "\n"

            # Finish constraint by adding either equality to one or zero depending on whether this is a domestic
            # flight or not.
            if self.flights.domestic(i):
                c += " = 1\n"
            else:
                c += " = 0\n"

        return c

    def constraint_kq_after_6pm(self):
        c = "\\ Domestic flight constraints\n"
        time_6pm = time(hour=18)

        non_kq_gates = ['4', '5', '7', '8', '9', '10']
        for i, gate_name in enumerate(non_kq_gates):
            if gate_name in self.airport.gate_names:
                non_kq_gates[i] = self.airport.gate_names.index(gate_name)

        for i, k, flight in self.departing_flights():
            if (flight.etd >= time_6pm) and (self.flights.airline(i) == "KQ"):
                c += "k6_{}:\n".format(i)
                for l in non_kq_gates:
                    if self.airport.bay_gate_distance[k][l] is not None:
                        c += " +{:10s}".format(self.x(i, l))

                        # Add new line if necessary
                        if len(c.split("\n")[-1]) > self.line_width_limit:
                            c = c.rstrip()
                            c += "\n"

                # Finish constraint.
                c += " = 0\n"

        return c

