

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

        self.cols = [("idx", 3, None),
                     ("flight_type", 11, lambda x: str(x)),
                     ("in_flight_no", 12, None),
                     ("origin", 6, None),
                     ("eta", 5, lambda x: x.strftime("%H:%M")),
                     ("bay", 4, None),
                     ("gate", 4, None),
                     ("reg_no", 6, None),
                     ("out_flight_no", 13, None),
                     ("dest", 4, None),
                     ("etd", 5, lambda x: x.strftime("%H:%M")),
                     ("ac_type", 7, None)]

    def str_heading(self):
        s = ""
        for name, width, _ in self.cols:
            s += "{name:>{width}}  ".format(name=name, width=width)
        return s + "\n" + "="*len(s) + "\n"

    def str_data(self):

        s = ""
        for name, width, type_conversion in self.cols:
            value = getattr(self, name)
            value = "" if value is None else value
            if value is None:
                value = ""
            else:
                value = type_conversion(value) if type_conversion is not None else value
            s += "{name:>{width}}  ".format(name=value, width=width)
        return s + "\n"
