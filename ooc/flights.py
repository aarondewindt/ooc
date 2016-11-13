from collections import namedtuple
from enum import Enum
from os.path import abspath, join, normpath
from datetime import time


# DOM array containing the information whether a departure flight is domestic
# P array containing the number of passengers for each flight
# PARK Array containing the information whether a flight is a ”Full’, Arrival, Parking or Departure activity’
# PREF array containing all preferences for each flight bay combination
# PREF2 array containing all preferences for each flight gate combination
# T Time Matrix containing the information whether flight pairs are conflicting
# TD Time Departure Matrix containing the information whether boarding activities of departing flight pairs are conflicting
# term index representing the check - in terminal

FlightType = namedtuple("FlightType",
                        ("flight_type",
                         "in_flight_no",
                         "origin",
                         "eta",
                         "bay",
                         "gate",
                         "reg_no",
                         "out_flight_no",
                         "dest",
                         "etd",
                         "ac_type"))
"""
Named tuple used to hold flight information
"""


class ft(Enum):
    """
    Enumerator used to represent the flight type.
    """
    Full = 0
    Arr = 1
    Park = 2
    Dep = 3


class Flights:
    """
    Class holding all information regarding the flights.

    :param string flight_data_path: PAth to directory holding flight data.
    """

    def __init__(self, flight_data_path):
        self.airport = None
        """
        class:`ooc.Airport` object.
        """

        # Get absolute path to flight data in case a relative path was given.
        # This is to prevent any future bugs which may be caused by switching the
        # current working directory.
        flight_data_path = abspath(flight_data_path)

        self.flight_data_path = normpath(join(flight_data_path, "flight_data.csv"))
        """Path to csv file holing the flight data."""

        self.flight_data = []

        # load data
        self.load_flight_data()

    def load_flight_data(self):
        with open(self.flight_data_path) as f:
            self.flight_data.clear()

            # Read the first line
            # Split the line at the commas
            # Strip any leading or trailing spaces, tabs, etc.
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["flight_type",
                           "in_flight_no",
                           "origin",
                           "eta",
                           "bay",
                           "gate",
                           "reg_no",
                           "out_flight_no",
                           "dest",
                           "etd",
                           "ac_type"]:
                raise Exception("Invalid flight_data csv file '{}'.".format(self.flight_data_path))

            # Read line by line.
            for line in f:
                # Split and strip values.
                line_values = [None if y == "" else y for y in [x.strip() for x in line.split(",")]]

                flight = FlightType(flight_type=ft[line_values[0]],  # Get ft enumerator.
                                    in_flight_no=line_values[1],
                                    origin=line_values[2],
                                    eta=time(*[int(x) for x in line_values[3].split(":")]),  # create time obj from eta
                                    bay=line_values[4],
                                    gate=line_values[5],
                                    reg_no=line_values[6],
                                    out_flight_no=line_values[7],
                                    dest=line_values[8],
                                    etd=time(*[int(x) for x in line_values[9].split(":")]),  # create time obj from etd
                                    ac_type=line_values[10])
                self.flight_data.append(flight)

    @property
    def n_flights(self):
        """
        Number of flights.
        """
        return len(self.flight_data)

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
        This is not loaded from airport_data, but is the maximum capacity of aircraft type.
        :param int i: Flight index
        :return: Number of passengers per flight.
        :rtype: int
        """
        flight = self.flight_data[i]
        return self.airport.aircraft[flight.ac_type].n_passengers

    def airline(self, i):
        """
        :param int i: Flight index
        :return: Airline code
        :rtype: string
        """

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
        Derived from airport code in raw airport_data.
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


