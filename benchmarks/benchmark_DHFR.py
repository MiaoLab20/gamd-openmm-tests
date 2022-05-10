"""
Run a benchmark of simulation times to compare GaMD with ordinary OpenMM.
"""

import os
import time
from sys import stdout
import tempfile

import simtk.openmm.app as app
import simtk.openmm as mm
import simtk.unit as unit
import numpy as np

from gamd import parser
from gamd import gamdSimulation
from gamd import runners


time_step = 0.002*unit.picoseconds
temperature = 300.*unit.kelvin
friction_coefficient = 1/unit.picosecond
nonbonded_cutoff = 0.9*unit.nanometer
cudaDeviceIndex = "0"
THIS_DIRECTORY = os.path.dirname(__file__)
ROOT_DIRECTORY = os.path.join(THIS_DIRECTORY, "..")
system_folder = os.path.join(THIS_DIRECTORY, "../data")
#prmtop_filename = os.path.join(system_folder, "dip.prmtop")
#inpcrd_filename = os.path.join(system_folder, "dip.crd")
#pdb_filename = os.path.join(system_folder, "dip.pdb")
num_steps = 10000

pdb_filename = os.path.join(ROOT_DIRECTORY, "data/5dfr_solv-cube_equil.pdb")
ff = app.ForceField('amber99sb.xml', 'tip3p.xml')
mypdb = app.PDBFile(pdb_filename)
num_atoms = len(mypdb.getPositions())

def run_ordinary_openmm():
    system = ff.createSystem(mypdb.topology,
                             nonbondedMethod=app.PME, 
                             nonbondedCutoff=nonbonded_cutoff,
                             constraints=app.HBonds)
    integrator = mm.LangevinIntegrator(temperature, friction_coefficient, time_step)
    platform = mm.Platform.getPlatformByName('CUDA')
    properties = {'CudaDeviceIndex': cudaDeviceIndex, 'CudaPrecision': 'mixed'}
    simulation = app.Simulation(mypdb.topology, system, integrator, platform, 
        properties)
    simulation.context.setPositions(mypdb.positions)
    #simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)
    simulation.minimizeEnergy()
    simulation.context.setVelocitiesToTemperature(temperature)
    
    start_time = time.time()
    simulation.step(num_steps)
    total_time = time.time() - start_time
    simulation_in_ns = num_steps * time_step.value_in_unit(unit.picoseconds) * 1e-3
    total_time_in_days = total_time / (86400)
    ns_per_day = simulation_in_ns / total_time_in_days
    return ns_per_day
    
def run_gamd_openmm(sigma0=6.0):
    curdir = os.getcwd()
    os.chdir(ROOT_DIRECTORY)
    input_file = "data/dhfr_ff.xml"
    parserFactory = parser.ParserFactory()
    config = parserFactory.parse_file(input_file, "xml")
    config.integrator.number_of_steps.conventional_md_prep == 2000
    config.integrator.number_of_steps.conventional_md == 10000
    config.integrator.number_of_steps.gamd_equilibration_prep == 2000
    config.integrator.number_of_steps.gamd_equilibration == 20000
    config.integrator.number_of_steps.gamd_production == 30000
    config.integrator.number_of_steps.averaging_window_interval == 50
    config.integrator.sigma0.primary = sigma0 * unit.kilocalories_per_mole
    config.integrator.sigma0.secondary = sigma0 * unit.kilocalories_per_mole
    with tempfile.TemporaryDirectory() as temp_dir:
        config.outputs.directory = os.path.join(temp_dir)
        gamdSimulationFactory = gamdSimulation.GamdSimulationFactory()
        gamdSim = gamdSimulationFactory.createGamdSimulation(
            config, "cuda", cudaDeviceIndex)
        runner = runners.Runner(config, gamdSim, False)
        runner.run()
    
    ns_per_day = 0.0
    os.chdir(curdir)
    return ns_per_day
    
print("GaMD results for sigma0 = 6.0")
run_gamd_openmm(6.0)
print("GaMD results for sigma0 = 0.0")
run_gamd_openmm(0.0)
ns_per_day_ordinary = run_ordinary_openmm()
print("Ordinary OpenMM benchmark:", ns_per_day_ordinary, "ns/day")
print("Alanine dipeptide system has:", num_atoms, "atoms")

