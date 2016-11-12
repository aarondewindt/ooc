

class Airport:
    """
    class holding all information regarding the airport.
    """

    def __init__(self):
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
    def b(self):
        """
        Bay Compliance Matrix containing the information whether ac
        type and bay are compatible.
        """
        return

    @property
    def d2(self):
        """
        Array containing the distances from all bays to all the gates.
        """

    @property
    def f(self):
        """
        Array containing the information whether the bay has a fuel pit.
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
