from enum import Enum
from sys import stdout
from io import IOBase


def pr_r(prt): print("\033[91m{}\033[00m" .format(prt))  # red


def pr_g(prt): print("\033[92m{}\033[00m" .format(prt))  # green


def pr_y(prt): print("\033[93m{}\033[00m" .format(prt))  # yellow


def pr_lp(prt): print("\033[94m{}\033[00m" .format(prt))  # light purple


def pr_p(prt): print("\033[95m{}\033[00m" .format(prt))  # purple


def pr_c(prt): print("\033[96m{}\033[00m" .format(prt))  # cyan


def pr_lg(prt): print("\033[97m{}\033[00m" .format(prt))  # light gray


def pr_k(prt): print("\033[98m{}\033[00m" .format(prt))  # black

