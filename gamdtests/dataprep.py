import os
import csv
import subprocess


def run_provided_data_prep_command(execution_directory,
                                   command_str):
    print("Running command ", command_str, "in directory ", execution_directory)

    result = subprocess.run([command_str],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            cwd=execution_directory, shell=True)

    output_filename = os.path.join(execution_directory, "data-prep-output.txt")
    with open(output_filename, "w") as output:
        output.write(result.stdout)


def run_cpptraj_command(execution_directory,
                        relative_cpptraj_script_path,
                        data_file_path,
                        output_path):
    command_str = "cpptraj -p {} -i {}".format(data_file_path,
                                               relative_cpptraj_script_path)
    result = subprocess.run([command_str],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            cwd=execution_directory, shell=True)

    cpptraj_out = os.path.join(output_path, "cpptraj-output.txt")
    with open(cpptraj_out, "w") as output:
        output.write(result.stdout)


def get_analysis_paths(output_directory, coordinate_type):

    directory = os.path.join(output_directory, "analysis")
    rc_directory = os.path.join(directory, coordinate_type)
    relative_rc_directory = os.path.join("analysis", coordinate_type)
    command_filename = "cpptraj-commands.cpptraj"

    cmd_filepath = os.path.join(rc_directory, command_filename)
    data_filepath = os.path.join(rc_directory, "cpptraj-data.dat")

    relative_cmd_filepath = os.path.join(relative_rc_directory,
                                         command_filename)
    relative_data_filepath = os.path.join(relative_rc_directory,
                                          "cpptraj-data.dat")

    results = {"command-path": cmd_filepath,
               "relative-command-path": relative_cmd_filepath,
               "relative-data-filepath": relative_data_filepath,
               "data-filepath": data_filepath,
               "rc-directory": rc_directory,
               "relative-rc-directory": relative_rc_directory}

    return results


def write_out_1d_rc_cpptraj_command(output_directory, starting_frame,
                                    coordinate_type, cpptraj_command,
                                    boost_type_str):
    paths = get_analysis_paths(output_directory, coordinate_type)
    command_str = "dihedral {} {} {}\n".format(coordinate_type,
                                               cpptraj_command,
                                               paths["relative-data-filepath"])
    with open(paths["command-path"], "w") as dat_command_file:
        if boost_type_str != "gamd-cmd-base":
            dat_command_file.write(
                "trajin output.dcd " + str(int(starting_frame)) + "\n")
        else:
            dat_command_file.write("trajin output.dcd 1\n")

        dat_command_file.write(command_str)
        dat_command_file.write("go" + "\n")
    return paths


def write_out_2d_rc_cpptraj_command(output_directory, starting_frame,
                                    coordinate_type, coordinate_type1,
                                    coordinate_type2,
                                    cpptraj_command1,
                                    cpptraj_command2,boost_type_str):
    paths = get_analysis_paths(output_directory, coordinate_type)
    template_str = "dihedral {} {} {}\n"
    command_str1 = template_str.format(coordinate_type1, cpptraj_command1,
                                       paths["relative-data-filepath"])
    command_str2 = template_str.format(coordinate_type2, cpptraj_command2,
                                       paths["relative-data-filepath"])
    with open(paths["command-path"], "w") as dat_command_file:
        if boost_type_str != "gamd-cmd-base":
            dat_command_file.write(
                "trajin output.dcd " + str(int(starting_frame)) + "\n")
        else:
            dat_command_file.write("trajin output.dcd 1\n")

        dat_command_file.write(command_str1)
        dat_command_file.write(command_str2)
        dat_command_file.write("go" + "\n")
    return paths


def write_out_phi_cpptraj_command(output_directory, starting_frame,
                                  boost_type_str):
    paths = write_out_1d_rc_cpptraj_command(output_directory, starting_frame,
                                            "phi", ":1@C :2@N :2@CA :2@C out ",
                                            boost_type_str)
    return paths


def write_out_psi_cpptraj_command(output_directory, starting_frame,
                                  boost_type_str):
    paths = write_out_1d_rc_cpptraj_command(output_directory, starting_frame,
                                            "psi", ":2@N :2@CA :2@C :3@N out ",
                                            boost_type_str)
    return paths


def write_out_phi_psi_cpptraj_command(output_directory, starting_frame,
                                      boost_type_str):
    paths = write_out_2d_rc_cpptraj_command(output_directory, starting_frame,
                                            "phi-psi", "phi", "psi",
                                            ":1@C :2@N :2@CA :2@C out ",
                                            ":2@N :2@CA :2@C :3@N out ",
                                            boost_type_str)
    return paths


# noinspection DuplicatedCode
def write_out_and_run_cpptraj_command_files(output_directory, starting_frame,
                                            topology_filepath, boost_type_str=None):

    phi_paths = write_out_phi_cpptraj_command(output_directory, starting_frame,
                                              boost_type_str)
    psi_paths = write_out_psi_cpptraj_command(output_directory, starting_frame,
                                              boost_type_str)
    paths_2d = write_out_phi_psi_cpptraj_command(output_directory, starting_frame,
                                                 boost_type_str)
    paths = [phi_paths, psi_paths, paths_2d]
    for path in paths:
        run_cpptraj_command(output_directory, path["relative-command-path"],
                            topology_filepath, path["rc-directory"])
    results = [[phi_paths, psi_paths], [paths_2d]]
    return results


def output_function_1d(output_file, row):
    output_file.write("{}\n".format(row[1]))


def output_function_2d(output_file, row):
    output_file.write("{} {}\n".format(row[1], row[2]))


def prep_1d_cpptraj_output(filepath, output_directory):
    prep_cpptraj_output(filepath, output_directory, output_function_1d)


def prep_2d_cpptraj_output(filepath, output_directory):
    prep_cpptraj_output(filepath, output_directory, output_function_2d)


def prep_cpptraj_output(filepath, output_directory, output_function):
    output_filename = os.path.join(output_directory, "rc.dat")
    with open(filepath, "r") as datafile:
        datafile.readline()
        csvreader = csv.reader(datafile, delimiter=" ", skipinitialspace=True)
        with open(output_filename, "w") as output_file:
            for row in csvreader:
                output_function(output_file, row)


def perform_data_prep(output_directory, starting_frame, topology_filepath,
                      boost_type_str=None):
    data_files = write_out_and_run_cpptraj_command_files(output_directory,
                                                         starting_frame,
                                                         topology_filepath,
                                                         boost_type_str)
    paths_1d = data_files[0]
    paths_2d = data_files[1]
    for path in paths_1d:
        prep_1d_cpptraj_output(path["data-filepath"], path["rc-directory"])
    for path in paths_2d:
        prep_2d_cpptraj_output(path["data-filepath"], path["rc-directory"])


def create_weights_file(output_directory, temperature):
    gamd_reweighting_log = os.path.join(output_directory,
                                        "gamd-reweighting.log")
    weights_filename = os.path.join(output_directory, "weights.dat")
    ideal_gas_constant = 0.001987
    denominator = ideal_gas_constant * temperature
    with open(gamd_reweighting_log, 'r') as input_file:
        input_file.readline()
        input_file.readline()
        input_file.readline()
        reader = csv.reader(input_file, delimiter='\t', skipinitialspace=True)
        with open(weights_filename, "w") as weights_file:
            for row in reader:
                combined_boost_potential = float(row[7]) + float(row[8])
                field1 = combined_boost_potential/denominator
                result = "{} {} {}\n".format(field1, row[2],
                                             combined_boost_potential)
                weights_file.write(result)

