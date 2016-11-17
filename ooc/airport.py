from os.path import abspath, join, normpath
from collections import namedtuple, OrderedDict


AirlineType = namedtuple("AirlineType", ("group", "terminal"))
"""
Named tuple type holding the airline information.
"""

AircraftType = namedtuple("AircraftType", ("group", "n_passengers"))
"""
Named tuple type holding aircraft information.
"""


class Airport:
    """
    Class holding all information regarding the airport.

    :param string airport_data_path: Path a folder containing the csv
       files with the airport airport_data.
    """

    def __init__(self, airport_data_path):
        self.flights = None
        """
        :class:`ooc.Flights` object.
        """

        # Get absolute path to airport data in case a relative path was given.
        # This is to prevent any future bugs which may be caused by switching the
        # current working directory.
        airport_data_path = abspath(airport_data_path)

        # Create paths to individual data files.
        self.airlines_path = normpath(join(airport_data_path, "airlines.csv"))  #: Path to airlines csv file.
        self.aircraft_path = normpath(join(airport_data_path, "aircraft.csv"))  #: Path to aircraft csv file.
        self.bay_compliance_matrix_path = normpath(join(airport_data_path, "bay_compliance_matrix.csv"))
        """Path to the bay compliance matrix csv file."""
        self.bay_terminal_distance_path = normpath(join(airport_data_path, "bay_terminal_distance.csv"))
        """Path to the bay terminal distance csv file."""
        self.domestic_airports_path = normpath(join(airport_data_path, "domestic_airports.csv"))
        """Path to domestic airports csv file."""
        self.fueling_path = normpath(join(airport_data_path, "fueling.csv"))  #: Path to fueling csv file.
        self.gates_path = normpath(join(airport_data_path, "gates.csv"))  #: Path to fueling csv file.

        self.airlines = OrderedDict()  #: Dictionary holding airline information.
        self.aircraft = OrderedDict()  #: Dictionary holding aircraft information.
        self.bay_compliance_matrix = []
        """
        2D-list/dictionary holding the bay compliance matrix. The first index is the bay index. The second one
        is a dictionary key with the aircraft group.
        eg: self.bay_compliance_matrix[2]["C"]
        """

        self._bay_terminal_distance = OrderedDict()  #: Dictionary holding the bay terminal distance table

        self.gate_names = []  #: List holding the gate names.
        self.bay_names = []  #: List holding the bay names. Bay indices are based on this dictionary
        self.terminal_names = []  #: List holding the terminal names.
        self.domestic_airports = []  #: List of domestic airports.
        self.fueling = []  #: List containing booleans indicating whether a bay has fueling pits or not.

        # Load in data
        self.load_aircraft()
        self.load_bay_compliance_matrix()
        self.load_bay_terminal_distance()
        self.load_airlines()
        self.load_domestic_airports()
        self.load_fueling()
        self.load_gates()

    def load_airlines(self):
        """
        Loads in the airline data from the csv file.
        """
        with open(self.airlines_path) as f:
            # Clear airline dictionary.
            self.airlines.clear()

            # Read the first line
            # Split the line at the commas
            # Strip any leading or trailing spaces, tabs, etc.
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["airline", "group", "terminal"]:
                raise Exception("Invalid airline csv file '{}'.".format(self.airlines_path))

            # Read line by line.
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                # Check if terminal exists
                if line_values[2] not in self.terminal_names:
                    raise Exception("Invalid terminal '{}' for airline '{}'.".format(line_values[0],
                                                                                     line_values[2]))

                # Convert to integers and create AirlineType object.
                airline = AirlineType(group=int(line_values[1]),
                                      terminal=line_values[2])

                # Add it to the dictionary.
                if line_values[0] not in self.airlines:
                    self.airlines[line_values[0]] = airline
                else:
                    raise Exception("Airline '{}' has been defined multiple times in the airline csv file.". format(
                        line_values[0]
                    ))

    def load_aircraft(self):
        """
        Loads in the aircraft data from the csv file.
        """
        with open(self.aircraft_path) as f:
            self.aircraft.clear()

            # Read the heading
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["ac_type", "group", "n_passengers"]:
                raise Exception("Invalid aircraft csv file '{}'.".format(self.aircraft_path))

            # Read line by line.
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                # Create aircraft tuple.
                aircraft = AircraftType(group=line_values[1],
                                        n_passengers=int(line_values[2]))

                # Add it to the dictionary.
                self.aircraft[line_values[0]] = aircraft

    def load_bay_compliance_matrix(self):
        """
        Loads in the bay compliance matrix from the csv file.
        """
        with open(self.bay_compliance_matrix_path) as f:
            self.bay_compliance_matrix.clear()
            self.bay_names.clear()

            # Read the heading
            heading = [x.strip() for x in f.readline().split(",")]

            # No heading check this time, since we don't yet know
            # how many aircraft groups there are. These are defined
            # by this heading.

            aircraft_groups = heading[1:]

            # Read line by line.
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                # Create bay info dictionary
                bay_info = OrderedDict(zip(aircraft_groups,
                                           [bool(int(x)) for x in line_values[1:]]))

                # Add bay name to bay name list.
                self.bay_names.append(line_values[0])

                # Add it to the bay compliance dict.
                self.bay_compliance_matrix.append(bay_info)

    def load_bay_terminal_distance(self):
        with open(self.bay_terminal_distance_path) as f:
            # Reset bay_terminal_distance to a list of None's with the
            # length of self.bay_names.
            self._bay_terminal_distance = [None] * len(self.bay_names)
            self.terminal_names.clear()

            # Read the heading
            heading = [x.strip() for x in f.readline().split(",")]

            # No heading check this time, since we don't yet know
            # how many terminals there are. These are defined
            # by this heading.

            self.terminal_names = heading[1:]

            # Read line by line.
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                # Check if bay name is valid and get bay_index
                bay_name = line_values[0]
                if bay_name not in self.bay_names:
                    raise Exception("Bay '{}' in the bay terminal distance table is invalid".format(bay_name))
                bay_index = self.bay_names.index(bay_name)

                # Create bay info list
                # bay_info = [int(x) for x in line_values[1:]]
                bay_info = OrderedDict(zip(self.terminal_names,
                                           [float(x) for x in line_values[1:]]))

                # Add it to the bay compliance dict.
                self._bay_terminal_distance[bay_index] = bay_info

            # Check whether we have the information for all bays.
            missing = []
            for bay_index, bay_info in enumerate(self._bay_terminal_distance):
                if bay_info is None:
                    missing.append(self.bay_names[bay_index])
            if len(missing):
                raise Exception("Terminal distance information is missing for bays\n{}".format(missing))

    def load_domestic_airports(self):
        with open(self.domestic_airports_path) as f:
            self.domestic_airports.clear()

            # Loop line by line
            for line in f:
                # Strip line of leading and trailing spaces, tabs, etc, and append it to the list.
                self.domestic_airports.append(line.strip())

    def load_fueling(self):
        self.fueling = [None] * len(self.bay_names)

        with open(self.fueling_path) as f:
            # Read the first line
            # Split the line at the commas
            # Strip any leading or trailing spaces, tabs, etc.
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["bay", "fueling"]:
                raise Exception("Invalid fueling csv file '{}'.".format(self.airlines_path))

            # Read line by line
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                # Check whether bay is valid.
                if line_values[0] not in self.bay_names:
                    raise Exception("Invalid bay '{}' in the fueling csv.".format(line_values[0]))

                bay_index = self.bay_names.index(line_values[0])
                self.fueling[bay_index] = bool(int(line_values[1]))

            # Check whether we have the fueling information for all bays.
            missing = []
            for bay_index, bay_info in enumerate(self.fueling):
                if bay_info is None:
                    missing.append(self.bay_names[bay_index])
            if len(missing):
                raise Exception("Fueling information is missing for bays\n{}".format(missing))

    def load_gates(self):
        self.gate_names.clear()
        with open(self.gates_path) as f:
            # Read the first line
            # Split the line at the commas
            # Strip any leading or trailing spaces, tabs, etc.
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["gate"]:
                raise Exception("Invalid fueling csv file '{}'.".format(self.airlines_path))

            for line in f:
                self.gate_names.append(line.strip())


    def terminal_bay_distance(self, term, k):
        """
        :param string term: Terminal name.
        :param int k: Bay index
        :return: Distance between bay and terminal.
        :rtype: float
        """
        return self._bay_terminal_distance[k][term]

    @property
    def n_bays(self):
        """
        Number of bays at the airport.
        """
        return len(self.bay_names)

    @property
    def n_gates(self):
        """
        Number of gates at the airport.
        """
        return 0
