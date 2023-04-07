#!/bin/bash

if ! command -v PyReweighting-1D.py &> /dev/null
then
    echo "You need to add the PyReweighting programs to your path prior to running this script."
    exit
fi

if [ "$#" -lt 4 ]; then
    echo "Usage do-average-test.sh location-of-cmd-directory config-type run-type output-directory [quick]"
    echo "  location-of-cmd-directory:  Path containing the three conventional md runs."
    echo "  config-type:                The input config based on input type:  amber, charmm36, etc."
    echo "  run-type:                   boost type (lower-dual, upper-total, etc)"
    echo "  output-directory:           Path to place all of the output."
    echo "  quick:                      [Optional] Tells the program to use the config files in the short-debug-tests directories instead."
    exit 2
fi

Conventional_MD_Directory=$(realpath "$1")
CONFIG_TYPE=$2
RUN_TYPE=$3
OUTPUT_BASE=$4
QUICK=$5

if [ "$QUICK" == "quick" ]; then
  CONFIG_FILE="./tests/manual/short-debug-tests/alanine-dipeptide/$CONFIG_TYPE/$RUN_TYPE.xml"
  REWEIGHTING_FILE="./tests/manual/short-debug-tests/alanine-dipeptide/reweighting/$RUN_TYPE.ini"
else
  CONFIG_FILE="./tests/manual/full-acceptance-tests/alanine-dipeptide/$CONFIG_TYPE/$RUN_TYPE.xml"
  REWEIGHTING_FILE="./tests/manual/full-acceptance-tests/alanine-dipeptide/reweighting/$RUN_TYPE.ini"
fi

mkdir "$OUTPUT_BASE"

./testRunner xml "$CONFIG_FILE" -o "$OUTPUT_BASE"/1/ -a "$REWEIGHTING_FILE"
echo ""
./testRunner xml "$CONFIG_FILE" -o "$OUTPUT_BASE"/2/ -a "$REWEIGHTING_FILE"
echo ""
./testRunner xml "$CONFIG_FILE" -o "$OUTPUT_BASE"/3/ -a "$REWEIGHTING_FILE"

GRAPH_1D_APP=$(realpath ./create-1d-analysis-graph.py)
GRAPH_2D_APP=$(realpath ./create-2d-analysis-graph.py)

$GRAPH_2D_APP "$OUTPUT_BASE" "$REWEIGHTING_FILE"
cd  "$OUTPUT_BASE/"; $GRAPH_1D_APP "$Conventional_MD_Directory" "Conventional MD" ./ "$RUN_TYPE"; mv 1D-Phi.png "$RUN_TYPE"-1D-Phi.png; mv 1D-Psi.png "$RUN_TYPE"-1D-Psi.png; mv 2d-analysis/2D_Free_energy_surface.png "$RUN_TYPE"-2D_Free_energy_surface.png



