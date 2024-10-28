#################################################################
# Sandia National Labs
# Date: 11-08-2021
# Author: Kelsie Larson
# Department: 06321
# Contact: kmlarso@sandia.gov
#
# Entry point to the SILT application.  Also store version #.
#################################################################

import sys
import importlib.metadata
from .mainwindow import run

__version__ = importlib.metadata.version("silt")


def main():
    run(sys.argv)
