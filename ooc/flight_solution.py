

# To be honest, I'm kinda regretting the decision I took in the beginning to not use SQL.

class FlightSolution:
    """This class holds the solution of a single flight."""
    def __init__(self, idx):
        self.idx = idx
        self.flight_type = None  #:
        self.in_flight_no = None  #:
        self.origin = None  #:
        self.eta = None  #:
        self.reg_no = None  #:
        self.out_flight_no = None  #:
        self.dest = None  #:
        self.etd = None  #:
        self.ac_type = None  #:

        self.bay = None  #: Assigned bay
        self.gate = None  #: Assigned gate

        self.bay_idx = None  #: Assigned bay index
        self.gate_idx = None  #: Assigned gate index

        self.cols = [("idx", 3),
                     ("in_flight_no", 12),
                     ("origin", 6),
                     ("eta", 5),
                     ("bay", 4),
                     ("gate", 4),
                     ("reg_no", 6),
                     ("out_flight_no", 13),
                     ("dest", 4),
                     ("etd", 5),
                     ("ac_type", 7)]

    def str_heading(self):
        s = ""
        for name, width in self.cols:
            s += "{name:>{width}}  ".format(name=name, width=width)
        return s + "\n" + "="*len(s) + "\n"

    def str_data(self):
        s = ""
        for name, width in self.cols:
            value = getattr(self, name)
            value = "" if value is None else value
            s += "{name:>{width}}  ".format(name=value, width=width)
        return s + "\n"
