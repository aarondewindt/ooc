

class GateAssignment:
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
