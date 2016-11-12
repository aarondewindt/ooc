from collections import namedtuple

# DOM array containing the information whether a departure flight is domestic
# P array containing the number of passengers for each flight
# PARK Array containing the information whether a flight is a ”Full’, Arrival, Parking or Departure activity’
# PREF array containing all preferences for each flight bay combination
# PREF2 array containing all preferences for each flight gate combination
# T Time Matrix containing the information whether flight pairs are conflicting
# TD Time Departure Matrix containing the information whether boarding activities of departing flight pairs are conflicting
# term index representing the check - in terminal

FlightType = namedtuple("FlightType", (""))


class Flights:
    """
    Class holding all information regarding the flights.
    """

    def __init__(self):
        self.airport = None
        """
        class:`ooc.Airport` object.
        """

    @property
    def n_flights(self):
        """
        Number of flights.
        """
        pass

    def flight_name(self, i):
        """
        Returns the name of a flight. This name consists of the flight number and type.
        :param int i: Flight index
        :return: Flight name
        :rtype: string
        """
        # TODO: Generate name out of table holding the flight information.
        return str(i)

    def n_passengers(self, i):
        """
        This is not loaded from data, but is the maximum capacity of aircraft type.
        :param int i: Flight index
        :return: Number of passengers per flight.
        :rtype: int
        """
        return

    def terminal(self, i):
        """
        Derived from airline group.
        :param int i: Flight index
        :return: Terminal index for this flight.
        """

    def preference(self, i, k):
        """

        :param int i: Flight index
        :return: Preference of flight bay combination.
        :rtype: float
        """

    def domestic(self, i):
        """
        Derived from airport code in raw data.
        :param int i: Flight index
        :return: True if it's a domestic flight
        :rtype: bool
        """

    def time_conflict(self, i, j):
        """
        :param i: Index of first flight
        :param j: Index of second flight
        :return: Returns True if the two fights conflict in time.
        """


