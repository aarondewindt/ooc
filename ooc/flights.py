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
                         "airline",
                         "preference",
                         "current"))
"""
Named tuple used to hold flight information
"""

PreferenceType = namedtuple("PreferenceType",
                            ("dest",
                             "bays",
                             "gates"))
"""
Named tuple used to hold flight preference information.
"""

CurrentType = namedtuple("CurrentType",
                         ("bay",))
"""
Named tuple used to hold the current location of overnight flights.
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

        self.flight_data_path = normpath(join(flight_data_path, "flight_schedule.csv"))
        """Path to csv file holing the flight data."""

        self.preferences_path = normpath(join(flight_data_path, "preferences.csv"))
        """Path to csv file holing the flight bay and gate preference table."""

        self.current_path = normpath(join(flight_data_path, "current.csv"))
        """Path to the csv file holding the position of the current location of overnight flights."""

        self.flight_schedule = []
        self.preferences_table = {}
        self.current_table = {}

        # load data
        self.load_current()
        self.load_preferences()
        self.load_flight_data()

    def load_flight_data(self):
        with open(self.flight_data_path) as f:
            self.flight_schedule.clear()

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
                raise Exception("Invalid flight schedule csv file '{}'.".format(self.flight_data_path))

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
                                                                                              len(self.flight_schedule)))

                # If this flight has neither an inbound nor outbound flight number, than get the airline code from the
                # last read flight. This happens for park flights and departure flights at the end of the day.
                if airline_code is None:
                    airline_code = self.flight_schedule[-1].airline

                # Find flight preference.
                flight_nos = [line_values[1], line_values[7]]
                flight_preference = None
                for flight_no in flight_nos:
                    if flight_no is None:
                        continue
                    for flight_pref_no in self.preferences_table:
                        if flight_no.startswith(flight_pref_no) and line_values[8] == self.preferences_table[flight_pref_no].dest:
                            flight_preference = self.preferences_table[flight_pref_no]
                            break
                    if flight_preference is not None:
                        break

                # Find current location if known.
                current_location = None
                for flight_no in [line_values[1], line_values[7]]:
                    if flight_no is None:
                        continue
                    if flight_no in self.current_table:
                        current_location = self.current_table[flight_no]

                # Create flight object.
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
                                    airline=airline_code,
                                    preference=flight_preference,
                                    current=current_location)

                # Check if the aircraft type is valid
                if flight.ac_type not in self.airport.aircraft:
                    raise Exception("Invalid aircraft type '{}' for flight '{}'.".format(flight.ac_type,
                                                                                         len(self.flight_schedule)))

                self.flight_schedule.append(flight)

    def load_preferences(self):
        """
        Loads in data from the preferences csv file.
        :return:
        """
        with open(self.preferences_path) as f:
            self.preferences_table.clear()

            # Read the first line
            # Split the line at the commas
            # Strip any leading or trailing spaces, tabs, etc.
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["flight", "dest", "bays", "gates"]:
                raise Exception("Invalid preferences csv file '{}'.".format(self.preferences_path))

            # Read line by line
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                preference = PreferenceType(dest=line_values[1],
                                            bays=tuple([self.airport.bay_names.index(x.strip()) for x in line_values[2].split(";")]),
                                            gates=tuple([self.airport.gate_names.index(x.strip()) for x in line_values[3].split(";")]))
                self.preferences_table[line_values[0]] = preference

    def load_current(self):
        """
        Loads in data from the current csv file.

        :return:
        """
        with open(self.current_path) as f:
            self.current_table.clear()

            # Read the first line
            # Split the line at the commas
            # Strip any leading or trailing spaces, tabs, etc.
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["flight", "bay"]:
                raise Exception("Invalid current csv file '{}'.".format(self.preferences_path))

            # Read line by line
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                bay_index = self.airport.bay_names.index(line_values[1].strip())

                current = CurrentType(bay=bay_index)
                self.current_table[line_values[0]] = current

    @property
    def n_flights(self):
        """
        Number of flights.
        """
        return len(self.flight_schedule)

    def n_passengers(self, i):
        """
        This is not loaded from airport_data, but is the maximum capacity of aircraft type.

        :param int i: Flight index
        :return: Number of passengers per flight.
        :rtype: int
        """
        flight = self.flight_schedule[i]
        return self.airport.aircraft[flight.ac_type].n_passengers

    def airline(self, i):
        """
        :param int i: Flight index
        :return: Airline code
        :rtype: string
        """
        # First check the inbound flight number for the airline code.
        # If there is no inbound flight number than check the outbound.
        if self.flight_schedule[i].airline is None:
            raise Exception("Flight '{}' has neither in inbound or outbound flight number.".format(i))
        else:
            return self.flight_schedule[i].airline

    def terminal(self, i):
        """
        Returns the terminal name based on the airline and puts all domestic flights on terminal D.

        :param int i: Flight index
        :return: Terminal index for this flight.
        """

        # If it's a domestic flight then put it on terminal D. Otherwise from the terminal information.
        if self.domestic(i):
            return "D"
        else:
            airline_code = self.airline(i)
            return self.airport.airlines[airline_code].terminal

    def domestic(self, i):
        """
        Derived from airport code in raw airport_data. It first checks the origin airport. If no

        :param int i: Flight index
        :return: True if it's a domestic flight
        :rtype: bool
        """

        if self.flight_schedule[i].flight_type in [ft.Full, ft.Arr]:
            # If this a full flight or arrival, check the origin
            # airport first. If no origin airport was given check
            # the destination airport.
            airport_codes = [self.flight_schedule[i].origin,
                             self.flight_schedule[i].dest]
        else:
            # If this is a parking or departure flight, then check
            # the destination first. If it's missing check the origin.
            airport_codes = [self.flight_schedule[i].dest,
                             self.flight_schedule[i].origin]

        for airport_code in airport_codes:
            if airport_code is not None:
                return airport_code in self.airport.domestic_airports

        # If this point was reached, than neither a origin nor destination
        # airport was given.
        raise Exception("Flight '{}' has neither a origin or outbound airport.")

    def departing(self, i):
        """
        :param i: Flight index
        :return: Boolean indicating whether this is a departing flight.
        """
        return self.flight_schedule[i].flight_type in [ft.Full, ft.Dep] and \
               self.flight_schedule[i].out_flight_no is not None

    def time_conflict(self, i, j):
        """
        :param i: Index of first flight
        :param j: Index of second flight
        :return: Returns True if the two fights conflict in time.
        """

        fi = self.flight_schedule[i]
        fj = self.flight_schedule[j]

        # Some long stay flights are parked during the night to the next day.
        if (fi.eta < fi.etd) and (fj.eta < fj.etd):
            # Neither is a overnight flight.
            return (fi.eta <= fj.etd) and (fj.eta <= fi.etd)

        elif (fi.eta >= fi.etd) and (fj.eta <= fj.etd):
            # flight i is an overnight flight.
            return (fi.eta <= fj.etd) or (fj.eta <= fi.etd)

        elif (fi.eta <= fi.etd) and (fj.eta >= fj.etd):
            # flight j is an overnight flight.
            return (fj.eta <= fi.etd) or (fi.eta <= fj.etd)

        else:
            # Both are overnight flights, so they are time conflicting.
            return True

    def bay_compliance(self, i, k):
        """
        :param int i: Flight index
        :param int k: Bay index
        :return: True if the aircraft type for this flight complies with the bay used.
        """
        ac_group = self.airport.aircraft[self.flight_schedule[i].ac_type].group
        return self.airport.bay_compliance_matrix[k][ac_group]

    def is_overnight(self, i):
        """
        :param i: Flight id
        :return: A boolean indicating whether a flight is an overnight flight or not.
        """
        f = self.flight_schedule[i]
        if f.flight_type == ft.Full:
            return f.etd < f.eta
        if f.flight_type == ft.Arr:
            return (f.etd < f.eta) or \
                   (self.flight_schedule[i+1].etd < self.flight_schedule[i+1].eta) or \
                   (self.flight_schedule[i+2].etd < self.flight_schedule[i+2].eta)

    def beta(self):
        beta = 0
        for i in range(self.n_flights):
            max_distance = self.airport.max_distance[self.terminal(i)]
            n_passengers = self.n_passengers(i)
            beta += max_distance * n_passengers
        return beta

    def gamma(self):
        return self.beta() * 3
