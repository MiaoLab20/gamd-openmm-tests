
import os
import subprocess
from configparser import ConfigParser


def get_reweighting_configuration(configuration_filename):
    config = ConfigParser()
    config.read(configuration_filename)
    return config


def get_reaction_coordinate_groups(config):
    reaction_coordinate_groups = config.sections()
    return reaction_coordinate_groups


def get_one_and_two_dimension_groups(config):
    one_dimension_groups = []
    two_dimension_groups = []

    for section in config.sections():
        if config[section]["dimensions"] == "1":
            one_dimension_groups.append(section)
        elif config[section]["dimensions"] == "2":
            two_dimension_groups.append(section)

    result = [one_dimension_groups, two_dimension_groups]
    return result


def get_fit_string(reweighting_parameters):
    result = ""
    if reweighting_parameters["job"] == "amd_dV":
        result = "-fit " + reweighting_parameters["fit"]
    return result


def get_order_string(reweighting_parameters):
    result = ""
    if reweighting_parameters["job"] == "amdweight_MC":
        result = "-order " + reweighting_parameters["order"]
    return result


def create_1d_command_string(parameters, temperature, reweighting_log_file,
                             weights_file=None):
    if parameters["job"] != "noweight":
        fit = get_fit_string(parameters)
        order = get_order_string(parameters)
        command_template = "PyReweighting-1D.py -input {} -T {} -cutoff {} -Xdim {} -disc {} -Emax {} -job {} -weight {} {} {} | tee {}"
        if weights_file is None:
            weights_filepath = parameters["weight-file"]
        else:
            weights_filepath = weights_file

        command_str = command_template.format(parameters["input-file"],
                                              str(temperature),
                                              parameters["cutoff"],
                                              parameters["xdim"],
                                              parameters["disc"],
                                              parameters["emax"],
                                              parameters["job"],
                                              weights_filepath,
                                              fit,
                                              order,
                                              reweighting_log_file)
    else:
        command_template = "PyReweighting-1D.py -input {} -T {} -cutoff {} -Xdim {} -disc {} -Emax {} -job {} | tee {}"
        command_str = command_template.format(parameters["input-file"],
                                              str(temperature),
                                              parameters["cutoff"],
                                              parameters["xdim"],
                                              parameters["disc"],
                                              parameters["emax"],
                                              parameters["job"],
                                              reweighting_log_file)

    return command_str


def create_2d_command_string(parameters, temperature, reweighting_log_file,
                             weights_file=None):
    if parameters["job"] != "noweight":
        command_template = "PyReweighting-2D.py -input {} -T {} -cutoff {} -Xdim {} -discX {} -Ydim {} -discY {} -Emax {} -job {} -weight {} {} {}| tee {}"
        fit = get_fit_string(parameters)
        order = get_order_string(parameters)
        if weights_file is None:
            weights_filepath = parameters["weight-file"]
        else:
            weights_filepath = weights_file
        command_str = command_template.format(parameters["input-file"],
                                              str(temperature),
                                              parameters["cutoff"],
                                              parameters["xdim"],
                                              parameters["discX"],
                                              parameters["ydim"],
                                              parameters["discY"],
                                              parameters["emax"],
                                              parameters["job"],
                                              weights_filepath,
                                              fit,
                                              order,
                                              reweighting_log_file)
    else:
        command_template = "PyReweighting-2D.py -input {} -T {} -cutoff {} -Xdim {} -discX {} -Ydim {} -discY {} -Emax {} -job {} | tee {}"
        command_str = command_template.format(parameters["input-file"],
                                              str(temperature),
                                              parameters["cutoff"],
                                              parameters["xdim"],
                                              parameters["discX"],
                                              parameters["ydim"],
                                              parameters["discY"],
                                              parameters["emax"],
                                              parameters["job"],
                                              reweighting_log_file)
    return command_str


def run_reweighting(output_directory, reweighting_parameters, temperature,
                    coordinate_directory, reweighting_log_filename,
                    weights_file=None):
    dimensions = int(reweighting_parameters["dimensions"])
    if dimensions == 1:
        command = create_1d_command_string(reweighting_parameters, temperature,
                                           "reweighting-output-1D.log",
                                           weights_file)
    elif dimensions == 2:
        command = create_2d_command_string(reweighting_parameters, temperature,
                                           "reweighting-output-2D.log",
                                           weights_file)
    else:
        print("Error:  Can't do reweighting of dimensions:  ",
              dimensions)
        command = None

    # Run the command from within that directory.
    if command is not None:

        execution_directory = os.path.join(output_directory,
                                           coordinate_directory)

        result = subprocess.run([command],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                cwd=execution_directory, shell=True)
        reweighting_log_filepath = os.path.join(execution_directory,
                                                reweighting_log_filename)
        with open(reweighting_log_filepath, "w") as output:
            output.write(result.stdout)


def run_all_reweightings(output_directory, config, temperature, weights_file=None):

    reaction_coordinate_groups = get_reaction_coordinate_groups(config)

    for group in reaction_coordinate_groups:
        coordinate_directory = os.path.join("analysis", group)
        reweighting_log_filename = str(group) + "-reweighting.log"
        # Move the necessary files into that directory.
        run_reweighting(output_directory, config[group], temperature,
                        coordinate_directory,
                        reweighting_log_filename, weights_file)

