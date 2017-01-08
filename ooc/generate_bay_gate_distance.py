"""
This file is not part of the solver. Instead it was used to generate the bay gate distance matrix.
These distances are all based from measurements from google earth.





"""

from collections import OrderedDict
from io import StringIO

# Simplified airport layout used by this script to calculate the distances.
#
#    2                                   14      15       20
# +--+-----------------------------------+--+----+--------+
# |                                      |  21-25
# + STPV1/2                              |
# |                                      |
# |                                      |
# +---------+                  +---------+----------+
#    Hotel                       J1-J5      J6-J9
#    bays
#

# Approximate distance between gate 1 and the non-remote bays.
ds_nr = [
    None,
    0,
    55,
    112,
    158,
    221,
    250,
    304,
    369,
    409,
    461,
    528,
    569,
    616,
    671,
    777,
    821,
    885,
    909,
    947,
    1001,
]

# Distance between gate 14 and the juliet bays
ds_j = [
    None,
    738,
    661,
    561,
    545,
    567,
    357,
    428,
    496,
    540,
]

# Distance between gate 1 and the hotel bays
ds_h = [
    None,
    778,
    824,
    869,
    912,
    957,
    1001,
    1047,
    1091,
    1135,
    1177,
]

# Distance between gate 1 and stpv
ds_stpv = 188

# Distance between gate 1 and bussing gates 21-25
# It's assumed that these gate are on the same line as the non remote bays. Between bays 14 and 15.
ds_bussing = 740


# Create dictionary containing the positions of each bay on the main line starting at H10 and ending at bay 20.

# Dictionary of bays and to what gates they are directly connected to or index in case of the remote bays.
bays = OrderedDict((
    ("2A", 2),
    ("2B", 2),
    ("2C", 2),
    ("3A", 3),
    ("3B", 3),
    ("3C", 3),
    ("4L", 4),
    ("4R", 4),
    ("5", 5),
    ("6", 5),
    ("7", 7),
    ("8", 8),
    ("9", 9),
    ("10", 10),
    ("11", 10),
    ("12", 12),
    ("13", 13),
    ("14", 14),
    ("15", 15),
    ("16", 16),
    ("17", 17),
    ("18", 18),
    ("19", 19),
    ("20", 20),
    ("J1", 1),
    ("J2A", 2),
    ("J2B", 2),
    ("J3A", 3),
    ("J3B", 3),
    ("J4A", 4),
    ("J4B", 4),
    ("J5", 5),
    ("J6", 6),
    ("J7", 7),
    ("J8", 8),
    ("J9", 9),
    ("H1", 1),
    ("H2", 2),
    ("H3", 3),
    ("H4", 4),
    ("H5", 5),
    ("H6", 6),
    ("H7", 7),
    ("H8", 8),
    ("H9", 9),
    ("H10", 10),
))


bay_gate_distance = OrderedDict()

for bay_name, i in bays.items():
    if bay_name.startswith("H"):
        # Position relative to gate 1
        pg1 = -1 * ds_h[i]

        # Array holding the distance to each gate.
        ds_gates = []

        # Add distance to normal gates
        for j in range(1, 21):
            if j in [3, 6, 11]:
                ds_gates.append("x")
            else:
                ds_gates.append(str(abs(pg1 - ds_nr[j])))

        # Add distance to bussing gates.
        for j in range(21, 26):
            ds_gates.append(str(abs(pg1 - ds_bussing)))

        bay_gate_distance[bay_name] = ds_gates


    elif bay_name.startswith("J"):
        # Position relative to gate 14
        pg14 = ds_j[i]

        # Array holding the distance to each gate.
        ds_gates = []

        # Add distance to normal gates
        for j in range(1, 21):
            if j in [3, 6, 11]:
                ds_gates.append("x")
            else:
                ds_gates.append(str(abs(ds_nr[j] - ds_nr[14]) + pg14))

        # Add distance to bussing gates.
        for j in range(21, 26):
            ds_gates.append(str(ds_bussing - ds_nr[14] + pg14))

        bay_gate_distance[bay_name] = ds_gates



    elif bay_name.startswith("STPV"):
        # Not implemented
        pass
    else:
        # distance to gate 1
        dsg1 = ds_nr[i]

        # Array holding the distance to each gate.
        ds_gates = []

        # Add distance to normal gates
        for j in range(1, 21):
            if j in [3, 6, 11]:
                ds_gates.append("x")
            else:
                ds_gates.append(str(abs(dsg1-ds_nr[j])))

        # Add distance to bussing gates.
        for j in range(21, 26):
            ds_gates.append(str(abs(dsg1 - ds_bussing)))

        bay_gate_distance[bay_name] = ds_gates

# StringIO used to build the final table
sio = StringIO()

# Write header

sio.write("bay, ")


def gate_header():
    """Yield strings containing the names of each gate."""
    for i in range(1, 26):
        yield "{:4}".format(i)

sio.write(", ".join(gate_header()))
sio.write("\n")

for bay_name, ds_gates in bay_gate_distance.items():
    def foo():
        for i in range(0, 25):
            yield "{:>4}".format(ds_gates[i])
    sio.write("{:3}, ".format(bay_name))
    sio.write(", ".join(foo()))
    sio.write("\n")

print(sio.getvalue())