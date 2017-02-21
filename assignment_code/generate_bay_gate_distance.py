"""
This file is not part of the model. Instead it was used to generate the bay gate distance table.
These distances are all based from measurements from google earth.

"""

from collections import OrderedDict
from io import StringIO


# The simplified airport layout used by this script to calculate the distances.
#
#    2                                  14   21-25  15       20
# +--+----------------------------------+----+------+--------+
# |                                          |
# + STPV1/2                                  |
# |                                          |
# |                                          |
# +---------+                      +---------+----------+
#    Hotel                           J1-J5      J6-J9
#    bays
#


# Distance between gate 1 and the other gates and non-remote bays.
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

# Distance between gates 21/25 and the juliet bays
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
    ("SPV1", None),
    ("SPV2", None),
))


bay_gate_distance = OrderedDict()

inactive_gates = [3]
non_existing_gates = [6, 11]

# Loop through all bays
for bay_name, i in bays.items():
    if bay_name.startswith("H"):  # Check whether this is a Hotel bay.
        # Position relative to gate 1
        pg1 = -1 * ds_h[i]

        # Array holding the distance to each gate.
        ds_gates = []

        # Add distance to normal gates
        for j in range(1, 21):
            if j in non_existing_gates:
                pass
            elif j in inactive_gates:
                ds_gates.append("x")
            else:
                ds_gates.append(str(abs(pg1 - ds_nr[j])))

        # Add distance to bussing gates.
        for j in range(21, 26):
            ds_gates.append(str(abs(pg1 - ds_bussing)))

        bay_gate_distance[bay_name] = ds_gates

    elif bay_name.startswith("J"):  # Check whether ths is a Juliet bay.
        # Position relative to bussing area
        pg14 = ds_j[i]

        # Array holding the distance to each gate.
        ds_gates = []

        # Add distance to normal gates
        for j in range(1, 21):
            if j in non_existing_gates:
                pass
            elif j in inactive_gates:
                ds_gates.append("x")
            else:
                ds_gates.append(str(abs(ds_nr[j] - ds_bussing) + pg14))

        # Add distance to bussing gates.
        for j in range(21, 26):
            ds_gates.append(str(pg14))

        bay_gate_distance[bay_name] = ds_gates

    elif bay_name.startswith("SPV"):  # Check whether this is a state pavilion bay
        # Array holding the distance to each gate.
        ds_gates = []

        # Add distance to normal gates
        for j in range(1, 21):
            if j in non_existing_gates:
                pass
            elif j in inactive_gates:
                ds_gates.append("x")
            else:
                ds_gates.append(str(ds_stpv + ds_nr[j]))

        # Add distance to bussing gates.
        for j in range(21, 26):
            ds_gates.append(str(ds_stpv + ds_bussing))

        bay_gate_distance[bay_name] = ds_gates
    else:  # This is a non-remote bay.
        # distance to gate 1
        dsg1 = ds_nr[i]

        # Array holding the distance to each gate.
        ds_gates = []

        # Add distance to normal gates
        for j in range(1, 21):
            if j in non_existing_gates:
                pass
            elif j in inactive_gates:
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
sio.write("bay , ")


def gate_header():
    """Generator yielding strings containing the names of each gate."""
    for i in range(1, 26):
        if i in non_existing_gates:
            continue
        i = " 20B" if i == 25 else i
        yield "{:4}".format(i)

sio.write(", ".join(gate_header()))
sio.write("\n")

# Loop through each bay.
for bay_name, ds_gates in bay_gate_distance.items():
    def foo():
        """Generator yielding the distance to each gate."""
        for i in range(0, 23):
            yield "{:>4}".format(ds_gates[i])
    sio.write("{:4}, ".format(bay_name))
    sio.write(", ".join(foo()))
    sio.write("\n")

# Print the final table.
print(sio.getvalue())

with open("jomo_kenyatta_international_airport/bay_gate_distance.csv", "w") as f:
    f.write(sio.getvalue())
