"""
Test gamd_openmm's ability to restart interrupted simulations.
"""

import os
import glob
import signal

import pytest
from simtk import unit
import mdtraj

from gamd import parser
from gamd import gamdSimulation
from gamd import runners

TEST_DIRECTORY = os.path.dirname(__file__)
ROOT_DIRECTORY = os.path.join(TEST_DIRECTORY, "..")

def make_simulation_restart(tmp_path, gamd_production_steps=None):
    os.chdir(ROOT_DIRECTORY)
    input_file = os.path.join(TEST_DIRECTORY, "../data/dip_amber.xml")
    parserFactory = parser.ParserFactory()
    config = parserFactory.parse_file(input_file, "xml")
    if gamd_production_steps is not None:
        config.integrator.number_of_steps.gamd_production = gamd_production_steps
        config.integrator.number_of_steps.compute_total_simulation_length()
    
    config.outputs.directory = os.path.join(
        tmp_path, "test_amber_alanine_dipeptide_runner_tiny_output")
    gamdSimulationFactory = gamdSimulation.GamdSimulationFactory()
    gamdSim = gamdSimulationFactory.createGamdSimulation(
        config, "reference", "")
    runner = runners.Runner(config, gamdSim, False)
    return runner

def trajectory_and_log_same_size(config):
    trajectory_glob = os.path.join(config.outputs.directory, "output*dcd")
    trajectory_files = glob.glob(trajectory_glob)
    top_file = os.path.join(ROOT_DIRECTORY, "data/dip.pdb")
    traj = mdtraj.load(trajectory_files, top=top_file)
    gamd_log_file = os.path.join(config.outputs.directory, "gamd.log")
    gamd_log_line_counter = 0
    with open(gamd_log_file, "r") as f:
        for line in f.readlines():
            if not line.startswith("#"):
                gamd_log_line_counter += 1
                
    return gamd_log_line_counter == traj.n_frames
        

def test_uninterrupted_restart(tmp_path):
    """
    Test if a calculation can be restarted if the user simply wants
    to extend a finished simulation - not because of an unexpected
    interruption.
    """
    runner = make_simulation_restart(tmp_path)
    runner.run()
    same_number = trajectory_and_log_same_size(runner.config)
    assert same_number == True
    
    new_runner = make_simulation_restart(tmp_path, 40000)
    new_runner.run(restart=True)
    same_number = trajectory_and_log_same_size(runner.config)
    assert same_number == True

def handler(signum, frame):
    print("Sudden, unexpected interruption!")
    raise Exception("The system experienced an interruption.")

def test_interrupted_restart(tmp_path):
    """
    Test if a calculation can be restarted if the simulation was
    suddenly interrupted.
    """
    runner = make_simulation_restart(tmp_path)
    try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(5)
        runner.run()
    except (Exception, SystemExit):
        pass
        
    #same_number = trajectory_and_log_same_size(runner.config)
    #assert same_number == True
    
    new_runner = make_simulation_restart(tmp_path)
    new_runner.run(restart=True)
    same_number = trajectory_and_log_same_size(runner.config)
    assert same_number == True