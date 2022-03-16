#!/usr/bin/env python

import sys
import os

from gamdtests.reweighting import run_all_reweightings
from gamdtests.reweighting import get_reweighting_configuration


def get_temperature(directory):
    filename = os.path.join(directory, "temperature.dat")
    with open(filename, "r") as temperature_file:
        temperature = temperature_file.readline()

    return float(temperature.split()[0])


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
        sys.exit(1)

    gamd_results_directory = os.path.abspath(sys.argv[1])
    if len(sys.argv) == 3:
        config_filename = sys.argv[2]
    else:
        config_filename = os.path.join(gamd_results_directory,
                                       "reweighting.ini")

    config = get_reweighting_configuration(config_filename)
    temperature = get_temperature(gamd_results_directory)
    weights_filename = os.path.join(gamd_results_directory,
                                    "weights.dat")

    run_all_reweightings(gamd_results_directory, config, temperature,
                         weights_filename)


def usage():
    print("Usage:  run-reweightings gamd-results-directory")


if __name__ == "__main__":
    main()
