#!/bin/bash

if ! command -v PyReweighting-1D.py &> /dev/null
then
    echo "You need to add the PyReweighting programs to your path prior to running this script."
    exit
fi

if [ "$#" -lt 3 ]; then
    echo "Usage do-average-test.sh location-of-cmd-directory run-type output-directory [quick]"
    exit 2
fi

Conventional_MD_Directory=$(realpath "$1")
RUN_TYPE=$2
OUTPUT_BASE=$3
QUICK=$4

if [ "$QUICK" == "quick" ]; then
  CONFIG_FILE="./tests/manual/short-debug-tests/alanine-dipeptide/$RUN_TYPE.xml"
  REWEIGHTING_FILE="./tests/manual/short-debug-tests/alanine-dipeptide/$RUN_TYPE.ini"
else
  CONFIG_FILE="./tests/manual/full-acceptance-tests/alanine-dipeptide/$RUN_TYPE.xml"
  REWEIGHTING_FILE="./tests/manual/full-acceptance-tests/alanine-dipeptide/$RUN_TYPE.ini"
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
cd  "$OUTPUT_BASE/"; $GRAPH_1D_APP "$Conventional_MD_Directory" "Conventional MD" ./ "$RUN_TYPE"; mv 1D-Phi.png "$RUN_TYPE"-1D-Phi.png; mv 1D-Psi.png "$RUN_TYPE"-1D-Psi.png


