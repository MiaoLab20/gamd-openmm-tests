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
    
def run_gamd_openmm(sigma0=6.0, stage1_steps=2000, stage2_steps=10000, 
                    stage3_steps=2000, stage4_steps=20000, stage5_steps=30000,
                    boost_type="lower-dual"):
    curdir = os.getcwd()
    os.chdir(ROOT_DIRECTORY)
    input_file = "data/dhfr_ff.xml"
    parserFactory = parser.ParserFactory()
    config = parserFactory.parse_file(input_file, "xml")
    config.integrator.boost_type = boost_type
    config.integrator.number_of_steps.conventional_md_prep == stage1_steps
    config.integrator.number_of_steps.conventional_md == stage2_steps
    config.integrator.number_of_steps.gamd_equilibration_prep == stage3_steps
    config.integrator.number_of_steps.gamd_equilibration == stage4_steps
    config.integrator.number_of_steps.gamd_production == stage5_steps
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
    
if __name__ == "__main__":
    print("GaMD results for stage1 only.")
    run_gamd_openmm(sigma0=6.0, 
                    stage1_steps=60000,
                    stage2_steps=0,
                    stage3_steps=0,
                    stage4_steps=0,
                    stage5_steps=0,
                    boost_type="lower-dual")
    
    print("GaMD results for stage1 + stage2.")
    run_gamd_openmm(sigma0=6.0, 
                    stage1_steps=200,
                    stage2_steps=60000,
                    stage3_steps=0,
                    stage4_steps=0,
                    stage5_steps=0,
                    boost_type="lower-dual")
                    
    print("GaMD results for stages 1, 2, & 3.")
    run_gamd_openmm(sigma0=6.0, 
                    stage1_steps=200,
                    stage2_steps=400,
                    stage3_steps=60000,
                    stage4_steps=0,
                    stage5_steps=0,
                    boost_type="lower-dual")
                    
    print("GaMD results for stages 1, 2, & 3.")
    run_gamd_openmm(sigma0=6.0, 
                    stage1_steps=200,
                    stage2_steps=400,
                    stage3_steps=200,
                    stage4_steps=60000,
                    stage5_steps=0,
                    boost_type="lower-dual")
                    
    print("GaMD results for lower-dual.")
    run_gamd_openmm(sigma0=6.0, 
                    boost_type="lower-dual")
    
    print("GaMD results for lower-dihedral.")
    run_gamd_openmm(sigma0=6.0, 
                    boost_type="lower-dihedral")
                    
    print("GaMD results for lower-total.")
    run_gamd_openmm(sigma0=6.0, 
                    boost_type="lower-total")
    ns_per_day_ordinary = run_ordinary_openmm()
    print("Ordinary OpenMM benchmark:", ns_per_day_ordinary, "ns/day")
    print("Alanine dipeptide system has:", num_atoms, "atoms")

