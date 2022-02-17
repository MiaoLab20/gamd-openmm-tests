from gamd.runners import Runner
import shutil
import subprocess
import os


def create_graphics(execution_directory, command,
                    temperature, output_filename):

    result = subprocess.run(["/bin/bash " + command + " " + " " +
                             str(temperature)], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            cwd=execution_directory, shell=True)

    with open(output_filename, "w") as output:
        output.write(result.stdout)


def run_post_simulation(unitless_temperature, output_directory, starting_frame):
    graphics_log = os.path.join(output_directory, "graphics.log")
    shutil.copy("graphics/create-graphics.sh", output_directory + "/")
    write_out_cpptraj_command_files(output_directory, starting_frame)
    shutil.copytree("data", output_directory + "/data")
    create_graphics(output_directory, "create-graphics.sh",
                    str(unitless_temperature),
                    graphics_log)


def write_out_cpptraj_command_files(output_directory, starting_frame):
    write_out_phi_cpptraj_command(output_directory, starting_frame)
    write_out_psi_cpptraj_command(output_directory, starting_frame)
    write_out_phi_psi_cpptraj_command(output_directory, starting_frame)


def write_out_phi_cpptraj_command(output_directory, starting_frame):
    with open(output_directory + "/" + "phi-dat-commands.cpptraj",
              "w") as dat_command_file:
        dat_command_file.write(
            "trajin output.dcd " + str(int(starting_frame)) + "\n")
        dat_command_file.write(
            "dihedral phi :1@C :2@N :2@CA :2@C out graphics/phi-cpptraj.dat"
            + "\n")
        dat_command_file.write("go" + "\n")


def write_out_psi_cpptraj_command(output_directory, starting_frame):
    with open(output_directory + "/" + "psi-dat-commands.cpptraj", "w") as dat_command_file:
        dat_command_file.write(
            "trajin output.dcd " + str(int(starting_frame)) + "\n")
        dat_command_file.write(
            "dihedral psi :2@N :2@CA :2@C :3@N out graphics/psi-cpptraj.dat"
            + "\n")
        dat_command_file.write("go" + "\n")


def write_out_phi_psi_cpptraj_command(output_directory, starting_frame):
    with open(output_directory + "/" + "phi-psi-commands.cpptraj", "w") as dat_command_file:
        dat_command_file.write(
            "trajin output.dcd " + str(int(starting_frame)) + "\n")
        dat_command_file.write(
            "dihedral phi :1@C :2@N :2@CA :2@C out graphics/phi-psi-cpptraj.dat"
            + "\n")
        dat_command_file.write(
            "dihedral psi :2@N :2@CA :2@C :3@N out graphics/phi-psi-cpptraj.dat"
            + "\n")
        dat_command_file.write("go" + "\n")


class PostSimulationTestRunner(Runner):

    def run_post_simulation(self, temperature, output_directory,
                            production_starting_frame):
        run_post_simulation(temperature, output_directory,
                            production_starting_frame)

