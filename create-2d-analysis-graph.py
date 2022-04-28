#!/usr/bin/env python


import os
import sys

from gamdtests import analysis
from gamdtests import reweighting


def usage(appname):
    print(
        "\nThis program is meant to take a single directory that contains \n"
        "more than one directory containing simulations, where each simulation has \n"
        "a cpptraj ouput with an rc.dat in the analysis/phi-psi directory \n"
        "and a gamd-reweighting.log file in the simulation directory.  It \n"
        "will combine the appropriate files are run the 2D Pyreweighting in \n"
        "the original passed directory.\n")
    print("Usage:")
    print("{}:  directory reweighting.ini".format(appname))


def main():
    appname = sys.argv[0]
    number_of_arguments = len(sys.argv)
    if number_of_arguments != 3 or sys.argv[1] == "--help" or sys.argv[1] == "-h":
        usage(appname)
        sys.exit(1)

    rc_dat_filepath = "analysis/phi-psi/rc.dat"
    weights_file = "weights.dat"

    directory = sys.argv[1]
    reweighting_filepath = sys.argv[2]
    analysis_directory = os.path.join(directory, "2d-analysis")
    simulation_directories = analysis.determine_group_or_single_directory(directory)

    if len(simulation_directories) < 2:
        usage(appname)
        sys.exit(1)

    os.makedirs(analysis_directory, 0o755, True)

    temperature = analysis.get_temperature(simulation_directories[0])

    combined_rc_dat_file = os.path.join(analysis_directory, "rc.dat")
    combined_weights_filepath = os.path.join(analysis_directory, weights_file)
    analysis.concatenate_files_ignoring_hash_lines(simulation_directories,
                                                   rc_dat_filepath,
                                                   combined_rc_dat_file)
    analysis.concatenate_files_ignoring_hash_lines(simulation_directories,
                                                   weights_file,
                                                   combined_weights_filepath)

    config = reweighting.get_reweighting_configuration(reweighting_filepath)
    groups = reweighting.get_one_and_two_dimension_groups(config)
    two_dimension_groups = groups[1]
    for group in two_dimension_groups:
        reweighting_log_filename = str(group) + "-reweighting.log"
        reweighting.run_reweighting(analysis_directory, config[group], temperature, "./",
                                    reweighting_log_filename, weights_file)


if __name__ == '__main__':
    main()
