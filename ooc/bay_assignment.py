
# z1 bay objective function containing the passenger transport distance
# z2 bay objective function containing the flight preferences
# z3 bay objective function containing the penalty values for repositioning
# z4 total bay objective function excluding penalty values
# z5 total bay objective function including penalty values


class BayAssignment:
    """
    This class generated the lp code for the bay assignment problem.

    :param ooc.Airport airport: Airport object holding the information
    regarding the target airport.

    :param ooc.Flights: Flight object holding the information on all
        the flights of the day.
    """

    def __init__(self, airport, flights):
        self.airport = airport
        """"
        class:`ooc.Airport` object of holding the information of
        the target airport.
        """

        self.flights = flights
        """
        class:`ooc.Flights` object holding the information of all
        flights of the day
        """

        self.decision_vars_flight_bay = []
        """
        List holding the names of all the binary decision variables
        connecting flights with bays.
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

    def of_min_passenger_transport_distance(self):
        """
        :return: Objective function for minimizing passenger transport
           between the check-in terminal and bay. aka z1.
        :rtype: string
        """
        # Initialize string that will hold the object function
        z1 = "// Minimization of passenger transport distance\n"

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
                z1 += "    - {:20.8f} {}\n".format(constant, self.dv_fb_name(i, k))

        return z1

    def of_max_airline_preference(self):
        """
        :return: Objective function for maximizing airline bay preference.
        :rtype: string
        """
        # Initialize empty string that will hold the objective function.
        z2 = "// Maximization of airline preference\n"

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
                z2 += "    + {:20.8f} {}\n".format(constant, self.dv_fb_name(i, k))

    def penalty_values(self):
        """
        :return: Objective function with the summation of all penalty values U, V, W.
        """
        return "// Penalty values\n" \
               "    + {constant:20.8f} U \n" \
               "    + {constant:20.8f} V \n" \
               "    + {constant:20.8f} W \n".format(constant=self.gamma)

    def objective_function(self):
        """
        :return: The total bay assignment objective function.
        :rtype: string
        """
        # Crete total objective function by concatenating the individual objective
        # objective functions with newlines in between and adding `max:` and `;` to
        # the front and back.
        return "max:\n{}\n{}\n{};\n".format(self.of_min_passenger_transport_distance(),
                                            self.of_max_airline_preference(),
                                            self.penalty_values())

    def dv_fb_name(self, i, k):
        """
        Returns the name of the decision variable connecting a flight ``i``
        with bay ``k``.

        :param int i: Index representing the flight
        :param int k: Index representing the bay
        :return: The name of the binary decision variable
        """
        # Generate name.
        name =  "X_{}_{}".format(self.flights.flight_name(i),
                                 self.airport.bay_name(k))

        # Add it to the desition variable name list if it's not in there already.
        if name not in self.decision_vars_flight_bay:
            self.decision_vars_flight_bay.append(name)

        return name