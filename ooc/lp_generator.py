
# i index representing the flight
# k index representing the bay
# l index representing the gate

# S penalty value for adjacency constraints

# U variable containing the the number of towings from arrival to parking in the night shift
# V array containing the number of towings from parking to departure
# W variable containing the number of towings during day time
# X Binary Decision Variable


# z6 gate objective function containing the passenger transport distance
# z7 gate objective function containing the flight preferences
# z8 gate objective function containing the penalty values representing double scheduled gates
# z9 Total gate objective function


class LpGenerator:
    """
    Class that generates lp code for lp_solve that solves the bay and
    gate assignment.

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

