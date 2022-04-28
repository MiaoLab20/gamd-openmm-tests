import os
import sys


def get_directories(directory):
    directories = []
    files = os.listdir(directory)
    for file in files:
        if (file != "analysis" and file != "2d-analysis" and
                os.path.isdir(os.path.join(directory, file))):
            directories.append(os.path.join(directory, file))
    return directories


def determine_group_or_single_directory(directory):
    analysis_test = os.path.join(directory, "analysis")
    if os.path.exists(analysis_test) and os.path.isdir(analysis_test):
        simulation_directories = [directory]
    elif os.path.exists(directory):
        simulation_directories = get_directories(directory)
    else:
        print("{} is not a directory and should be".format(directory))
        sys.exit(-1)

    return simulation_directories


def concatenate_files_ignoring_hash_lines(directories, source_path, destination_path):
    with open(destination_path, "w") as destination_file:
        for directory in directories:
            filename = os.path.join(directory, source_path)
            with open(filename, "r") as source_data:
                lines = source_data.readlines()
                for line in lines:
                    if line[0] != '#':
                        destination_file.write(line)


def get_temperature(directory):
    filepath = os.path.join(directory, "temperature.dat")
    with open(filepath, "r") as temperature_file:
        line = temperature_file.readline()
        temperature = line.split()[0]
    return temperature
