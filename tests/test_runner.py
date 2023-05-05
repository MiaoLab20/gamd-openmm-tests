"""
test_runner.py

Test the runner.py module.
"""

import os

import pytest
from simtk import unit

from gamd import parser
from gamd import gamdSimulation
from gamd import runners

TEST_DIRECTORY = os.path.dirname(__file__)
ROOT_DIRECTORY = os.path.join(TEST_DIRECTORY, "..")

def test_amber_alanine_dipeptide_runner_tiny(tmp_path):
    """
    
    """
    os.chdir(ROOT_DIRECTORY)
    input_file = os.path.join(TEST_DIRECTORY, "../data/dip_amber.xml")
    parserFactory = parser.ParserFactory()
    config = parserFactory.parse_file(input_file, "xml")
    config.integrator.number_of_steps.conventional_md_prep == 10
    config.integrator.number_of_steps.conventional_md == 20
    config.integrator.number_of_steps.gamd_equilibration_prep == 10
    config.integrator.number_of_steps.gamd_equilibration == 20
    config.integrator.number_of_steps.gamd_production == 30
    config.integrator.number_of_steps.averaging_window_interval == 2
    config.outputs.directory = os.path.join(
        tmp_path, "test_amber_alanine_dipeptide_runner_tiny_output")
    gamdSimulationFactory = gamdSimulation.GamdSimulationFactory()
    gamdSim = gamdSimulationFactory.createGamdSimulation(
        config, "reference", "")
    runner = runners.Runner(config, gamdSim, False)
    runner.run()
    
def test_gromacs_peptide_runner_tiny(tmp_path):
    """
    
    """
    os.chdir(ROOT_DIRECTORY)
    input_file = os.path.join(TEST_DIRECTORY, "../data/gromacs/peptide-gromacs.xml")
    parserFactory = parser.ParserFactory()
    config = parserFactory.parse_file(input_file, "xml")
    config.integrator.number_of_steps.conventional_md_prep == 10
    config.integrator.number_of_steps.conventional_md == 20
    config.integrator.number_of_steps.gamd_equilibration_prep == 10
    config.integrator.number_of_steps.gamd_equilibration == 20
    config.integrator.number_of_steps.gamd_production == 30
    config.integrator.number_of_steps.averaging_window_interval == 2
    config.outputs.directory = os.path.join(
        tmp_path, "test_gromacs_peptide_runner_tiny_output")
    gamdSimulationFactory = gamdSimulation.GamdSimulationFactory()
    gamdSim = gamdSimulationFactory.createGamdSimulation(
        config, "reference", "")
    runner = runners.Runner(config, gamdSim, False)
    runner.run()
