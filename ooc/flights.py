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
                         "ac_type",
                         "airline"))
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
    :param ooc.Airport airport: Airport object holding airport specific information.
    """

    def __init__(self, flight_data_path, airport):
        self.airport = airport
        """
        class:`ooc.Airport` object.
        """

        # Attach to airport object.
        airport.flights = self

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

                # Get and check airline code. If neither an inbound
                # nor outbound flight number was given, set airline
                # code to None.
                airline_code = None
                for fl_no in [line_values[1],   # Inbound flight number
                              line_values[7]]:  # Outbound flight number
                    if fl_no is not None:  # If there is a flight number get airline code.
                        airline_code = fl_no[:2]
                        # Check whether the airline code was defined in the airlines csv file.
                        if airline_code not in self.airport.airlines:
                            raise Exception("Airline '{}' for flight '{}' is invalid.".format(airline_code,
                                                                                              len(self.flight_data)))

                # If this flight has neither an inbound nor outbound flight number that get the airline from the
                # last read airline. This happens for park flights and departure flights at the end of the day.
                if airline_code is None:
                    airline_code = self.flight_data[-1].airline

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
                                    ac_type=line_values[10],
                                    airline=airline_code)

                # Check if the aircraft type is valid
                if flight.ac_type not in self.airport.aircraft:
                    raise Exception("Invalid aircraft type '{}' for flight '{}'.".format(flight.ac_type,
                                                                                         len(self.flight_data)))

                self.flight_data.append(flight)

    @property
    def n_flights(self):
        """
        Number of flights.
        """
        return len(self.flight_data)

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
        # First check the inbound flight number for the airline code.
        # If there is no inbound flight number than check the outbound.
        if self.flight_data[i].airline is None:
            raise Exception("Flight '{}' has neither in inbound or outbound flight number.".format(i))
        else:
            return self.flight_data[i].airline

    def terminal(self, i):
        """
        Derived from airline group.
        :param int i: Flight index
        :return: Terminal index for this flight.
        """
        airline_code = self.airline(i)
        return self.airport.airlines[airline_code].terminal

    def preference(self, i, k):
        """
        :param int i: Flight index
        :return: Preference of flight bay combination.
        :rtype: float
        """
        # TODO: Figure this one out.
        return 1

    def domestic(self, i):
        """
        Derived from airport code in raw airport_data. It first checks the origin airport. If no
        :param int i: Flight index
        :return: True if it's a domestic flight
        :rtype: bool
        """

        if self.flight_data[i].flight_type in [ft.Full, ft.Arr]:
            # If this a full flight or arrival, check the origin
            # airport first. If no origin airport was given check
            # the destination airport.
            airport_codes = [self.flight_data[i].origin,
                             self.flight_data[i].dest]
        else:
            # If this is a parking or departure flight, then check
            # the destination first. If it's missing check the origin.
            airport_codes = [self.flight_data[i].dest,
                             self.flight_data[i].origin]

        for airport_code in airport_codes:
            if airport_code is not None:
                return airport_code in self.airport.domestic_airports

        # If this point was reached, than neither a origin nor destination
        # airport was given.
        raise Exception("Flight '{}' has neither a origin or outbound airport.")

    def time_conflict(self, i, j):
        """
        :param i: Index of first flight
        :param j: Index of second flight
        :return: Returns True if the two fights conflict in time.
        """

        fi = self.flight_data[i]
        fj = self.flight_data[j]

        return ((fi.eta < fj.eta) and (fj.eta < fi.etd)) or \
               ((fi.eta < fj.etd) and (fj.etd < fi.etd))

    def bay_compliance(self, i, k):
        """
        :param int i: FLight index
        :param int k: Bay index
        :return: True if the aircraft type for this flight complies with the bay used.
        """
        ac_group = self.airport.aircraft[self.flight_data[i].ac_type].group
        return self.airport.bay_compliance_matrix[k][ac_group]
