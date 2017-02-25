# ooc
This repository contains the code used to complete the assignment for the 
AE4441-16 operations optimization course. The topic chosen for this assignment
was based on J.O. Deken's master thesis: Robust Scheduling for the Bay and 
Gate Assignment, A Kenya Airways Case Study.

Repository url: https://github.com/aarondewindt/ooc

Authors
=======
 - Aaron M. de Windt
 - Kyana Shayan


Requirements
============
This code was written and tested with Python 3.6. compatibility with 
older versions of python is not guaranteed.

Dependencies
 - numpy
 - scipy
 - matplotlib
 - recordclass
 - Cplex (interactive solver)


Repository structure
====================
There are three directories in this repositories

 - test:            Contains python unittests to test different components of 
                    the program.
                    
 - ooc:             Main program sources. The code in here load in the data, 
                    generate the lp code and process the results.
                    
 - assignment_code: This directory contains the input data and the main source 
                    file of the assignment. This file calls the code in ooc and
                    gives it the appropriate input data.


Running the assignment code
===========================
The assignment code can be started by running the `main.py` file in the `assignment_code`
directory.

If the solver cannot find cplex it is possible to give it a path with the location
of the **cplex interactive solver** executable. For example:

```
solver = BayGateSolver(
        abs_path("jomo_kenyatta_international_airport"),
        abs_path("schedule_2015_07_05"),
        jid="workspace_2015_07_05",
        buffer_time=timedelta(minutes=15),
        spare_bays=['J3A', 'J3B'],
        
        cplex_command="path/to/cplex.exe"  # <---
    )
```
