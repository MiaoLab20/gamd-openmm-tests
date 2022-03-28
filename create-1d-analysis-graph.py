#!/usr/bin/env python

import sys
import os
import matplotlib.pyplot as plt
from pprint import pprint
from gamdtests import analysis


def usage(appname):
    print(
        "This program is meant to take an arbitrary number of directories"
        "containing simulations and an associated name and put them"
        "into a single graph for comparison.\n")
    print("Usage:")
    print("{}:  directory \"name\" directory \"name\" ...".format(appname))


def is_number(candidate):
    try:
        float(candidate)
    except ValueError:
        return False
    return True


def get_coordinates_from_file(filepath):
    with open(filepath, "r") as input_file:
        lines = input_file.readlines()
    result = {}
    x_values = []
    y_values = []
    for line in lines:
        fields = line.split()
        if len(fields) > 0 and is_number(fields[0]):
            x_values.append(float(fields[0]))
            y_values.append(float(fields[1]))
    result["x"] = x_values
    result["y"] = y_values

    return result


def main():

    appname = sys.argv[0]
    number_of_arguments = len(sys.argv)
    simulation_sets = []
    if number_of_arguments < 3 or ((number_of_arguments-1) % 2 != 0):  # not even
        usage(appname)
        sys.exit(1)

    phi_filepath = "analysis/phi/pmf-c2-rc.dat.xvg"
    psi_filepath = "analysis/psi/pmf-c2-rc.dat.xvg"

    graph_title = None
    for entry in map(lambda x: x * 2, range(int(number_of_arguments / 2))):
        directory = sys.argv[entry + 1]
        name = sys.argv[entry + 2]
        simulation_directories = analysis.determine_group_or_single_directory(directory)
        pair = [name, simulation_directories]
        simulation_sets.append(pair)
        if graph_title is not None:
            graph_title = graph_title + " vs. " + name
        else:
            graph_title = name

    create_graphic(simulation_sets, phi_filepath, "Phi", graph_title)
    create_graphic(simulation_sets, psi_filepath, "Psi", graph_title)


#
# Driver method for creating the graphics from the coordinates in the
# directory for a given file type.
#
def create_graphic(simulation_sets, filepath, xlabel, graph_title):
    coordinates = gather_coordinates(filepath, simulation_sets)
    graph_values = create_averages_and_errors(coordinates)
    generate_graphic_file(graph_values, xlabel, graph_title)

#
#  Function that actually generates the image file.
#


def generate_graphic_file(coordinates, xlabel, graph_title):
    plt.figure(figsize=(10.24, 7.68), dpi=400)

    for coordinate in coordinates:
        plt.errorbar(coordinate["x-values"], coordinate["y-averages"],
                     yerr=coordinate["y-errors"],
                     capsize=1, errorevery=1,
                     alpha=0.5, label=coordinate["name"])

    plt.axis([-180, 180, 0, 8])
    plt.ylabel("PMF")
    plt.xlabel(xlabel)
    plt.legend()
    plt.title(graph_title)
    plt.savefig("1D-" + xlabel + ".png")
    plt.close()


#
# These are the routines used to calculate
# the averages, errors, and put things in an easy to access
# way for doing our graphing.
#

def create_averages_and_errors(coordinate_sets):
    results = []
    for entry in coordinate_sets:
        name = entry[0]
        coordinates = entry[1]

        x_values = []
        y_averages = []
        y_min_errors = []
        y_max_errors = []

        first_coordinate_set = coordinates[0]
        number_of_entries = len(first_coordinate_set['x'])
        coordinate_sets_have_equal_number_of_entries = True

        for coordinate_set in coordinates:
            if len(coordinate_set['x']) != number_of_entries:
                coordinate_sets_have_equal_number_of_entries = False
                break

        if coordinate_sets_have_equal_number_of_entries:
            for iterator in range(len(first_coordinate_set['x'])):
                x_values.append(first_coordinate_set['x'][iterator])
                y_values = calculate_average_and_errors(coordinates, "y",
                                                        iterator)
                y_averages.append(y_values[0])
                y_min_errors.append(y_values[1])
                y_max_errors.append(y_values[2])
        else:
            print("Error: uneven number of coordinates between files.")
            sys.exit(2)

        result_set = {"name": name, "x-values": x_values,
                      "y-averages": y_averages,
                      "y-errors": [y_min_errors, y_max_errors]}
        results.append(result_set)

    return results


def calculate_average_and_errors(coordinates, coordinate_type, entry):
    group = []
    for coordinate in coordinates:
        group.append(coordinate[coordinate_type][entry])

    average = sum(group) / len(group)
    minimum_error = average - min(group)
    maximum_error = max(group) - average

    return [average, minimum_error, maximum_error]


#
# These are the routines to gather the information from the different files.
#
#

def gather_coordinates(filepath, simulation_sets):
    results = []
    for simulation in simulation_sets:
        simulation_directories = simulation[1]
        simulation_name = simulation[0]
        coordinates_set = []
        for directory in simulation_directories:
            xvgfile = os.path.join(directory, filepath)
            coordinates = get_coordinates_from_file(xvgfile)
            coordinates_set.append(coordinates)
        pair = [simulation_name, coordinates_set]
        results.append(pair)
    return results


if __name__ == '__main__':
    main()
