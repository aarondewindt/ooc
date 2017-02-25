"""
The class in here loads in and processes the data about the flight schedule.
"""

from recordclass import recordclass
from enum import Enum
from os.path import abspath, join, normpath
from datetime import time, date, datetime, timedelta
import json


FlightType = recordclass("FlightType",
                         ("flight_type",
                          "in_flight_no",
                          "origin",
                          "eta",
                          "reg_no",
                          "out_flight_no",
                          "dest",
                          "etd",
                          "ac_type",
                          "airline",
                          "preference",
                          "current"))
"""
Named tuple used to hold the flight information
"""

PreferenceType = recordclass("PreferenceType",
                             ("dest",
                              "bays",
                              "gates"))
"""
Named tuple used to hold the flight preference information.
"""

CurrentType = recordclass("CurrentType",
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
    Class holding the information regarding the flights.

    :param string flight_data_path: Path to directory holding flight data.
    :param ooc.Airport airport: Airport object holding airport specific information.
    :param datetime.timedelta buffer_time: Amount of buffer time to add before and after
       each flight.
    """

    def __init__(self, flight_data_path, airport, buffer_time=None, spare_bays=None):
        self.airport = airport
        """
        class:`ooc.Airport` object.
        """
        # If no buffer time was given then, set it to zero.
        self.buffer_time = buffer_time or timedelta(0)

        self.spare_bays = []

        if spare_bays is not None:
            for bay_name in spare_bays:
                if bay_name not in self.airport.bay_names:
                    raise Exception("Spare bay '{}' is invalid.".format(bay_name))
                self.spare_bays.append(self.airport.bay_names.index(bay_name))

        # Attach flight object to airport object.
        airport.flights = self

        # Get the absolute path to flight data in case a relative path was given.
        # This is to prevent any future bugs which may be caused by switching the
        # working directory.
        flight_data_path = abspath(flight_data_path)

        self.flight_data_path = normpath(join(flight_data_path, "flight_schedule.csv"))
        """Path to the csv file holing the flight data."""

        self.preferences_path = normpath(join(flight_data_path, "preferences.csv"))
        """Path to the csv file holing the flight bay and gate preference table."""

        self.current_path = normpath(join(flight_data_path, "current.csv"))
        """Path to the csv file holding the position of the current location of overnight flights."""

        self.config_path = normpath(join(flight_data_path, "config.json"))
        """Path to the json file holding the schedule configuration parameters."""

        self.flight_schedule = []  #: List holding the flight schedule and information.
        self.preferences_table = {}  #: Dictionary holding the flight preference table.
        self.current_table = {}  #: Dictionary holding the current location of overninght flights.
        self.config = {}  #: Dictionary holding other properties about the schedule.

        # Load data files
        self.load_config()
        self.load_current()
        self.load_preferences()
        self.load_flight_data()
        self.check_duplicate_flights()
        self.process_overnight_flights()
        self.process_flight_preferences()

    def load_config(self):
        with open(self.config_path) as f:
            self.config = json.load(f)
            self.config['date'] = datetime.strptime(self.config['date'], "%Y %m %d").date()

    def load_flight_data(self):
        """
        Loads the flight schedule csv file.
        """
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

            line_nr = -1
            # Read line by line.
            for line in f:
                line_nr += 1
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



                # Find current location if known.
                current_location = None
                for flight_no in [line_values[1], line_values[7]]:
                    if flight_no is None:
                        continue
                    if flight_no in self.current_table:
                        current_location = self.current_table[flight_no]

                # Create flight object.
                flight = FlightType(flight_type=ft[line_values[0]],  # Get ft enumerator.,
                                    in_flight_no=line_values[1],
                                    origin=line_values[2],
                                    eta=datetime(*self.config['date'].timetuple()[:3], *[int(x) for x in line_values[3].split(":")]),  # create time obj from eta
                                    # bay=line_values[4],
                                    # gate=line_values[5],
                                    reg_no=line_values[6],
                                    out_flight_no=line_values[7],
                                    dest=line_values[8],
                                    etd=datetime(*self.config['date'].timetuple()[:3], *[int(x) for x in line_values[9].split(":")]),  # create time obj from etd
                                    ac_type=line_values[10],
                                    airline=airline_code,
                                    preference=None,
                                    current=current_location)

                # Check if the aircraft type is valid
                if flight.ac_type not in self.airport.aircraft:
                    raise Exception("Invalid aircraft type '{}' for flight '{}'.".format(flight.ac_type,
                                                                                         len(self.flight_schedule)))

                self.flight_schedule.append(flight)

    def load_preferences(self):
        """
        Loads in data from the preferences csv file.
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
        Loads in data from the current csv file, holding the current location of overnight flights.
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

    def process_flight_preferences(self):
        for i, flight in enumerate(self.flight_schedule):
            # Find flight_nos
            in_flight = [None, None]
            out_flight = [None, None]
            if flight.flight_type in [ft.Arr, ft.Park, ft.Dep]:
                j = [ft.Arr, ft.Park, ft.Dep].index(flight.flight_type)
                in_flight[0] = self.flight_schedule[i - j].in_flight_no
                in_flight[1] = self.flight_schedule[i - j].origin
                out_flight[0] = self.flight_schedule[i + 2 - j].out_flight_no
                out_flight[1] = self.flight_schedule[i + 2 - j].dest
            else:
                in_flight[0] = flight.in_flight_no
                in_flight[1] = flight.origin
                out_flight[0] = flight.out_flight_no
                out_flight[1] = flight.dest

            # Find flight preference.
            flight_preference = None
            for flight_no, airport_code in [in_flight, out_flight]:
                if flight_no is None:
                    continue
                for flight_pref_no in self.preferences_table:
                    if flight_no.startswith(flight_pref_no) and airport_code == self.preferences_table[flight_pref_no].dest:
                        flight_preference = self.preferences_table[flight_pref_no]
                        break
                if flight_preference is not None:
                    break

            self.flight_schedule[i].preference = flight_preference




    def process_overnight_flights(self):
        """
        Since the schedule does not have the date information for the flight's eta and etd they will
        all be loaded in on the same date. This is not true for overnight flights that arrived on the previous
        day. This function fixes the eta and etd dates for overnight flights.

        :return:
        """
        # Loop through all flights.
        for i, flight in enumerate(self.flight_schedule):
            # Check if it's an
            if self.is_overnight(i):
                if flight.flight_type == ft.Arr:
                    previous_part_overnight = False
                    for j in [2, 1, 0]:
                        if previous_part_overnight:
                            self.flight_schedule[i + j].eta -= timedelta(days=1)
                            self.flight_schedule[i + j].etd -= timedelta(days=1)
                        if self.flight_schedule[i+j].eta > self.flight_schedule[i+j].etd:
                            self.flight_schedule[i + j].eta -= timedelta(days=1)
                            previous_part_overnight = True
                if flight.flight_type == ft.Full:
                    self.flight_schedule[i].eta -= timedelta(days=1)

    def check_duplicate_flights(self):
        """
        Check for duplicate flights in the flight schedule data.
        """

        # Loop through all flight combinations
        for i in range(self.n_flights):
            for j in range(i+1, self.n_flights):
                # Checks whether the flight numbers, eta and etd of the two flights are the same.
                if (((self.flight_schedule[i].in_flight_no == self.flight_schedule[j].in_flight_no) and
                     (self.flight_schedule[i].in_flight_no is not None)) or
                    ((self.flight_schedule[i].out_flight_no == self.flight_schedule[j].out_flight_no) and
                     (self.flight_schedule[i].out_flight_no is not None))
                    ) and \
                        (self.flight_schedule[i].eta == self.flight_schedule[j].eta) and \
                        (self.flight_schedule[i].etd == self.flight_schedule[j].etd):
                    print("Warning: Duplicate flights {} {}".format(i, j))  # Print a warning

    @property
    def n_flights(self):
        """
        Number of flights.
        """
        return len(self.flight_schedule)

    def n_passengers(self, i):
        """
        Maximum passenger capacity for a specific flight.

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
        if self.domestic(i, departing=True):
            return "D"
        else:
            airline_code = self.airline(i)
            return self.airport.airlines[airline_code].terminal

    def domestic(self, i, departing=False):
        """
        Derived from airport code in raw airport_data. By default it first checks the origin airport.

        :param int i: Flight index
        :param bool departing: If true it will first check the destination airport code.
        :return: True if it's a domestic flight
        :rtype: bool
        """

        if self.flight_schedule[i].flight_type in [ft.Arr, ft.Park] and not departing:
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

        # Add buffer times.
        # Only add a preceding buffer time period to arrival and full flights.
        # Only add a trailing buffer time period to departure and full flights.
        fi_eta = fi.eta - (self.buffer_time if self.flight_schedule[i].flight_type in [ft.Arr, ft.Full] else timedelta(0))
        fj_eta = fj.eta - (self.buffer_time if self.flight_schedule[j].flight_type in [ft.Arr, ft.Full] else timedelta(0))
        fi_etd = fi.etd + (self.buffer_time if self.flight_schedule[i].flight_type in [ft.Dep, ft.Full] else timedelta(0))
        fj_etd = fj.etd + (self.buffer_time if self.flight_schedule[j].flight_type in [ft.Dep, ft.Full] else timedelta(0))

        # Some long stay flights are parked during the night to the next day.
        if (fi_eta < fi_etd) and (fj_eta < fj_etd):
            # Neither is a overnight flight.
            return (fi_eta <= fj_etd) and (fj_eta <= fi_etd)

        elif (fi_eta >= fi_etd) and (fj_eta <= fj_etd):
            # flight i is an overnight flight.
            return (fi_eta <= fj_etd) or (fj_eta <= fi_etd)

        elif (fi_eta <= fi_etd) and (fj_eta >= fj_etd):
            # flight j is an overnight flight.
            return (fj_eta <= fi_etd) or (fi_eta <= fj_etd)

        else:
            # Both are overnight flights, so they are time conflicting.
            return True

    def bay_compliance(self, i, k):
        """
        :param int i: Flight index
        :param int k: Bay index
        :return: True if the aircraft type for this flight complies with the bay used.
        """
        if k in self.spare_bays:
            return False
        ac_group = self.airport.aircraft[self.flight_schedule[i].ac_type].group
        return self.airport.bay_compliance_matrix[k][ac_group]

    def is_overnight(self, i):
        """
        :param i: Flight id
        :return: A boolean indicating whether a flight is an overnight flight or not.
        """

        f = self.flight_schedule[i]

        # This will be valid for general use.
        if f.flight_type == ft.Full:
            if f.eta.day != f.etd.day:
                return True
        else:
            i -= [ft.Arr, ft.Park, ft.Dep].index(f.flight_type)
            if (f.etd.day != f.eta.day) or \
                   (self.flight_schedule[i+1].etd.day != self.flight_schedule[i+1].eta.day) or \
                   (self.flight_schedule[i+2].etd.day != self.flight_schedule[i+2].eta.day):
                return True

        # Since the schedule does not contain information on which day the flights eta and etd are. The will
        # both be loaded in on the same day. This part of the function is used to detect overnight flights in
        # this scenario. This is then used by the process_overnight_flights() to fix the dates for overnight
        # flights.
        if f.flight_type == ft.Full:
            return f.etd < f.eta
        else:
            i -= [ft.Arr, ft.Park, ft.Dep].index(f.flight_type)
            return (f.etd < f.eta) or \
                   (self.flight_schedule[i+1].etd < self.flight_schedule[i+1].eta) or \
                   (self.flight_schedule[i+2].etd < self.flight_schedule[i+2].eta)

    def beta(self):
        return self.gamma() * 3

    def gamma(self):
        gamma = 0
        for i in range(self.n_flights):
            max_distance = self.airport.max_distance[self.terminal(i)]
            n_passengers = self.n_passengers(i)
            gamma += max_distance * n_passengers
        return gamma
