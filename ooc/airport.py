from collections import namedtuple, OrderedDict

AirlineType = namedtuple("AirlineType", ("group", "terminal"))


class Airport:
    """
    Class holding all information regarding the airport.

    :param string airlines_path: Path to csv file holding airline information.
    """

    def __init__(self, airlines_path):
        self.flights = None
        """
        :class:`ooc.Flights` object.
        """

        self.airlines_path = airlines_path
        self.airlines = OrderedDict()
        """Dictionary holding airline information."""

        self.load_airlines()

    def load_airlines(self):
        with open(self.airlines_path) as f:
            # Clear airline dictionary.
            self.airlines.clear()

            # Read the first line
            # Split the line at the commas
            # Strip any leading or trailing spaces, tabs, etc.
            heading = [x.strip() for x in f.readline().split(",")]

            # Check if the heading is valid.
            if heading != ["airline", "group", "terminal"]:
                raise Exception("Invalid airline csv file.")

            # Read line by line.
            for line in f:
                # Split and strip values.
                line_values = [x.strip() for x in line.split(",")]

                # Convert to integers and create AirlineType object.
                airline = AirlineType(group=int(line_values[1]),
                                      terminal=int(line_values[2]))

                # Add it to the dictionary.
                self.airlines[line_values[0]] = airline

    def load_aircrafts(self):
        pass

    def load_terminal_bay_distance(self):
        pass

    def terminal_bay_distance(self, term, k):
        """
        :param int term: Terminal index
        :param int k: Bay index
        :return: Distance between bay and terminal.
        :rtype: float
        """
        return

    @property
    def n_bays(self):
        """
        Number of bays at the airport.
        """
        pass

    @property
    def n_gates(self):
        """
        Number of gates at the airport.
        """
        pass

    def bay_name(self, k):
        """
        The name of a bay.
        :param int k: Bay index
        :return: Bay name
        :rtype: string
        """
        # TODO: Return the bay name out of a table.
        return str(k)
