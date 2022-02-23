from gamd.runners import Runner
import shutil
import subprocess
import os
import gamdtests.reweighting as reweighting
from gamdtests import dataprep
import openmm.unit as unit


def create_analysis_directories(output_directory, coordinates):
    analysis_directory = os.path.join(output_directory, "analysis")
    os.makedirs(analysis_directory, 0o755, True)
    for coordinate in coordinates:
        directory = os.path.join(analysis_directory, coordinate)
        os.makedirs(directory, 0o755, True)


def run_post_simulation(unitless_temperature, output_directory,
                        starting_frame, reweighting_ini_file=None,
                        analysis_data_prep_command=None):

    shutil.copytree("data", os.path.join(output_directory, "data"))
    dataprep.create_weights_file(output_directory, unitless_temperature)
    if analysis_data_prep_command is None:
        if reweighting_ini_file is not None:
            #
            #  This is the default line for our code path.  While it is
            #  possible that we could rework the code to be more generic and
            #  accept arbitrary names for passing to cpptraj, I'm going to hold
            #  off doing so until we need it.
            #

            print("Running default data preperation steps.")
            print("Running reweighting based on provided config, but "
                  "using calculated weights.dat file.")
            config = reweighting.get_reweighting_configuration(
                reweighting_ini_file)

            reweighting_groups = reweighting.get_reaction_coordinate_groups(
                config)

            create_analysis_directories(output_directory, reweighting_groups)

            dataprep.perform_data_prep(output_directory, starting_frame,
                                       "data/dip.prmtop")
            reweighting.run_all_reweightings(output_directory, config,
                                             unitless_temperature,
                                             "../../weights.dat")
        else:
            print("Reweighting not being performed.")

    else:
        #
        # For now, if we have different reaction coordinates than our default,
        # we will handle it with a custom data preperation program.
        #
        print("Running provide data preparation command.")
        dataprep.run_provided_data_prep_command(output_directory,
                                                analysis_data_prep_command)
        if reweighting_ini_file is not None:
            print("Running reweighting based on provided config file.")
            config = reweighting.get_reweighting_configuration(
                reweighting_ini_file)
            reweighting.run_all_reweightings(output_directory,
                                             config, unitless_temperature)
        else:
            print("Reweighting not being performed.")


class PostSimulationTestRunner(Runner):

    def __init__(self, config, gamdSim, debug, prep_command=None,
                 analysis_config_file=None):
        self.prep_command = prep_command
        self.analysis_config_file = analysis_config_file
        super(PostSimulationTestRunner, self).__init__(config, gamdSim, debug)

    def run_post_simulation(self, temperature, output_directory,
                            production_starting_frame):

        unitless_temperature = temperature.value_in_unit(unit.kelvin)
        if self.prep_command is not None:
            data_prep_command = os.path.join(output_directory,
                                             "prepare-data")
            shutil.copy(self.prep_command, data_prep_command)
            data_prep_command = "prepare-data"
        else:
            data_prep_command = None

        if self.analysis_config_file is not None:
            reweighting_file = os.path.join(output_directory,
                                            "reweighting.ini")
            shutil.copy(self.analysis_config_file, reweighting_file)
        else:
            reweighting_file = None

        run_post_simulation(unitless_temperature, output_directory,
                            production_starting_frame, reweighting_file,
                            data_prep_command)

