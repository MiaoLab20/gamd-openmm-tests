#!/usr/bin/env python3

import argparse
from configparser import ConfigParser


def get_input(name, request_string, default_value = None):
    if default_value is not None:
        input_string = "Enter the {} for {} [default: {}]: "
        prompt = input_string.format(request_string, name, default_value)
        result = (input(prompt) or default_value)
    else:
        input_string = "Enter the {} for {}: "
        prompt = input_string.format(request_string, name)
        result = None
        while result is None:
            result = input(prompt)
    return result


def request_and_add_values(config, name, dimensions):
    order = None
    y_dim = None
    disc_y = None
    fit = None

    print("\nName:  {}".format(name))
    input_file = get_input(name, "input file", "rc.dat")
    weight_file = get_input(name, "weight file", "weights.dat")
    job_type = get_input(name, "job type reweighting method", "amdweight_CE")
    if job_type == "amdweight_MC":
        order = get_input(name, "Order of Maclaurin series")
    elif job_type == "amd_dV":
        fit = get_input(name, "Fit deltaV distribution")

    e_max = get_input(name, "Emax", "100")
    cutoff = get_input(name, "cutoff", "100")
    x_dim = get_input(name, "Xdim", "-180 180")
    disc_x = get_input(name, "discX", "6")

    if dimensions == "2":
        y_dim = get_input(name, "Ydim", "-180 180")
        disc_y = get_input(name, "discY", "6")

    add_section(config, name, dimensions, input_file, weight_file, cutoff,
                e_max, job_type, x_dim, disc_x, y_dim, disc_y, fit, order)
    return config


def add_section(config, name, dimensions, input_file, weight_file, cutoff,
                e_max, job_type, x_dim, disc_x,
                y_dim=None, disc_y=None, fit=None, order=None):

    config.add_section(name)
    config.set(name, 'input-file', input_file)
    config.set(name, 'job', job_type)
    config.set(name, 'dimensions', str(dimensions))
    config.set(name, 'weights-file', weight_file)
    config.set(name, 'Xdim', str(x_dim))
    if dimensions == "1":
        config.set(name, 'disc', str(disc_x))
    elif dimensions == "2":
        config.set(name, 'discX', str(disc_x))
        config.set(name, 'Ydim', str(y_dim))
        config.set(name, 'discY', str(disc_y))
    else:
        print("Invalid number of dimensions provided.")

    config.set(name, 'cutoff', str(cutoff))
    config.set(name, 'Emax', str(e_max))

    if fit is not None:
        config.set(name, 'fit', str(fit))
    if order is not None:
        config.set(name, 'order', str(order))

    return config


def create_argparser():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "output_file", metavar="OUTPUT_FILE", type=str,
        help="The filename to store the output.")
    argparser.add_argument("-i", "--input_ini", dest="input_ini_filename",
                           default=False,
                           help="Restart simulation from backup checkpoint in "
                                "input file", type=str)
    return argparser


def main():
    argparser = create_argparser()
    args = argparser.parse_args()  # parse the args into a dictionary
    args = vars(args)
    output_file = args["output_file"]
    input_ini = args["input_ini_filename"]
    config = ConfigParser()
    if input_ini is not False:
        config.read(input_ini)

    print("The program will ask you a series of questions.  Just hit Enter to "
          "accept the default values in brackets, if it is available.\n")

    add_reaction_coordinate = input("Do you want to add another PyReweighting section[y/n]? ")
    while add_reaction_coordinate == "y":
        rc_name = input("Enter Reaction Coordinate name:")
        if rc_name is not None and rc_name != "":
            number_of_dimension = str(get_input(rc_name,
                                                "number of dimensions",
                                                "1"))
            request_and_add_values(config, rc_name, number_of_dimension)
        add_reaction_coordinate = input(
            "\nDo you want to add another PyReweighting section[y/n]? ")

    with open(output_file, 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    main()
