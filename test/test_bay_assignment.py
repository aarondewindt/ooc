import unittest
import os

from ooc import Airport, Flights, BayAssignment


def abs_path(rel_path):
    """
    Returns an absolute path to a file relative to this file.
    :param rel_path: PAth relative to this file
    :return: Absolute path
    """
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path))


class MyTestCase(unittest.TestCase):

    @unittest.skip
    def test_something(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        bay_assignment = BayAssignment(flights)

        of = bay_assignment.objective_function()
        self.assertIn(objective_function_part_1, of)
        self.assertIn(objective_function_part_2, of)

    @unittest.skip
    def test_lp_code(self):
        airport = Airport(abs_path("./airport_data"))
        flights = Flights(abs_path("./flight_data"), airport)
        bay_assignment = BayAssignment(flights)

        code = bay_assignment.lp_code()
        self.assertIn(objective_function_part_1, code)
        self.assertIn(objective_function_part_2, code)
        self.assertIn(binary_declaration_part_1, code)
        self.assertIn(binary_declaration_part_2, code)


objective_function_part_1 = """max:
// Minimization of passenger transport distance
     -       5700.0000 X_0_0      -       5700.0000 X_0_1      -       5700.0000 X_0_2      -       5400.0000 X_0_3      -       5400.0000 X_0_4
     -       5400.0000 X_0_5      -       4500.0000 X_0_6      -       4500.0000 X_0_7      -       4200.0000 X_0_8      -       3900.0000 X_0_9
     -       3600.0000 X_0_10     -       3300.0000 X_0_11     -       3000.0000 X_0_12     -       2700.0000 X_0_13     -       2400.0000 X_0_14
     -       2100.0000 X_0_15     -       1800.0000 X_0_16     -       1500.0000 X_0_17     -        900.0000 X_0_18     -          0.0000 X_0_19
     -        900.0000 X_0_20     -       1200.0000 X_0_21     -        900.0000 X_0_22     -        600.0000 X_0_23     -       7500.0000 X_0_24
     -       7200.0000 X_0_25     -       7200.0000 X_0_26     -       6900.0000 X_0_27     -       6900.0000 X_0_28     -       6600.0000 X_0_29
     -       6600.0000 X_0_30     -       6300.0000 X_0_31     -       6600.0000 X_0_32     -       6900.0000 X_0_33     -       7200.0000 X_0_34
     -       7200.0000 X_0_35     -      60000.0000 X_0_36     -      60000.0000 X_0_37     -      60000.0000 X_0_38     -      60000.0000 X_0_39
     -      60000.0000 X_0_40     -      60000.0000 X_0_41     -      60000.0000 X_0_42     -      60000.0000 X_0_43     -      60000.0000 X_0_44
     -      60000.0000 X_0_45     -       1500.0000 X_1_0      -       1500.0000 X_1_1      -       1500.0000 X_1_2      -       1200.0000 X_1_3
     -       1200.0000 X_1_4      -       1200.0000 X_1_5      -        600.0000 X_1_6      -        600.0000 X_1_7      -          0.0000 X_1_8
     -        300.0000 X_1_9      -        600.0000 X_1_10     -        900.0000 X_1_11     -       1200.0000 X_1_12     -       1500.0000 X_1_13
     -       1800.0000 X_1_14     -       2100.0000 X_1_15     -       2400.0000 X_1_16     -       2700.0000 X_1_17     -       3900.0000 X_1_18"""


objective_function_part_2 = """// Maximization of airline preference
     +          1.0000 X_0_0      +          1.0000 X_0_1      +          1.0000 X_0_2      +          1.0000 X_0_3      +          1.0000 X_0_4
     +          1.0000 X_0_5      +          1.0000 X_0_6      +          1.0000 X_0_7      +          1.0000 X_0_8      +          1.0000 X_0_9
     +          1.0000 X_0_10     +          1.0000 X_0_11     +          1.0000 X_0_12     +          1.0000 X_0_13     +          1.0000 X_0_14
     +          1.0000 X_0_15     +          1.0000 X_0_16     +          1.0000 X_0_17     +          1.0000 X_0_18     +          1.0000 X_0_19"""

binary_declaration_part_1 = """// Binary decision variables declaration
binary
    X_0_0     , X_0_1     , X_0_2     , X_0_3     , X_0_4     , X_0_5     , X_0_6     , X_0_7     , X_0_8     , X_0_9     ,
    X_0_10    , X_0_11    , X_0_12    , X_0_13    , X_0_14    , X_0_15    , X_0_16    , X_0_17    , X_0_18    , X_0_19    ,
    X_0_20    , X_0_21    , X_0_22    , X_0_23    , X_0_24    , X_0_25    , X_0_26    , X_0_27    , X_0_28    , X_0_29    ,
    X_0_30    , X_0_31    , X_0_32    , X_0_33    , X_0_34    , X_0_35    , X_0_36    , X_0_37    , X_0_38    , X_0_39    ,
    X_0_40    , X_0_41    , X_0_42    , X_0_43    , X_0_44    , X_0_45    , X_1_0     , X_1_1     , X_1_2     , X_1_3     ,
    X_1_4     , X_1_5     , X_1_6     , X_1_7     , X_1_8     , X_1_9     , X_1_10    , X_1_11    , X_1_12    , X_1_13    ,
    X_1_14    , X_1_15    , X_1_16    , X_1_17    , X_1_18    , X_1_19    , X_1_20    , X_1_21    , X_1_22    , X_1_23    ,
    X_1_24    , X_1_25    , X_1_26    , X_1_27    , X_1_28    , X_1_29    , X_1_30    , X_1_31    , X_1_32    , X_1_33    ,
    X_1_34    , X_1_35    , X_1_36    , X_1_37    , X_1_38    , X_1_39    , X_1_40    , X_1_41    , X_1_42    , X_1_43    ,
    X_1_44    , X_1_45    , X_2_0     , X_2_1     , X_2_2     , X_2_3     , X_2_4     , X_2_5     , X_2_6     , X_2_7     ,"""

binary_declaration_part_2 = """    X_66_14   , X_66_15   , X_66_16   , X_66_17   , X_66_18   , X_66_19   , X_66_20   , X_66_21   , X_66_22   , X_66_23   ,
    X_66_24   , X_66_25   , X_66_26   , X_66_27   , X_66_28   , X_66_29   , X_66_30   , X_66_31   , X_66_32   , X_66_33   ,
    X_66_34   , X_66_35   , X_66_36   , X_66_37   , X_66_38   , X_66_39   , X_66_40   , X_66_41   , X_66_42   , X_66_43   ,
    X_66_44   , X_66_45   , X_67_0    , X_67_1    , X_67_2    , X_67_3    , X_67_4    , X_67_5    , X_67_6    , X_67_7    ,
    X_67_8    , X_67_9    , X_67_10   , X_67_11   , X_67_12   , X_67_13   , X_67_14   , X_67_15   , X_67_16   , X_67_17   ,
    X_67_18   , X_67_19   , X_67_20   , X_67_21   , X_67_22   , X_67_23   , X_67_24   , X_67_25   , X_67_26   , X_67_27   ,
    X_67_28   , X_67_29   , X_67_30   , X_67_31   , X_67_32   , X_67_33   , X_67_34   , X_67_35   , X_67_36   , X_67_37   ,
    X_67_38   , X_67_39   , X_67_40   , X_67_41   , X_67_42   , X_67_43   , X_67_44   , X_67_45   , X_68_0    , X_68_1    ,
    X_68_2    , X_68_3    , X_68_4    , X_68_5    , X_68_6    , X_68_7    , X_68_8    , X_68_9    , X_68_10   , X_68_11   ,
    X_68_12   , X_68_13   , X_68_14   , X_68_15   , X_68_16   , X_68_17   , X_68_18   , X_68_19   , X_68_20   , X_68_21   ,
    X_68_22   , X_68_23   , X_68_24   , X_68_25   , X_68_26   , X_68_27   , X_68_28   , X_68_29   , X_68_30   , X_68_31   ,
    X_68_32   , X_68_33   , X_68_34   , X_68_35   , X_68_36   , X_68_37   , X_68_38   , X_68_39   , X_68_40   , X_68_41   ,
    X_68_42   , X_68_43   , X_68_44   , X_68_45  ;"""

if __name__ == '__main__':
    unittest.main()
