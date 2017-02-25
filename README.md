# ooc
This python package contains the code for the group assignment of 
AE4441-16 operations optimization course.


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
 - Cplex


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
The assignment code requires the ooc python package to be installed. To solve this
the 'main_no_install.py' can be called to run the code without having to install ooc.

