#!/bin/bash

boost_types=( "lower-dual" "upper-dual" "lower-dual-nonbonded-dihedral" "upper-dual-nonbonded-dihedral" "lower-nonbonded" "upper-nonbonded" "lower-total" "upper-total" "lower-dihedral" "upper-dihedral" )

if ! command -v PyReweighting-1D.py &> /dev/null
then
    echo "You need to add the PyReweighting programs to your path prior to running this script."
    exit
fi

if [ "$#" -lt 3 ]; then
    echo "Usage verify-all-tests.sh location-of-cmd-directory config-type output-directory [quick]"
    echo "  location-of-cmd-directory:  Path containing the three conventional md runs."
    echo "  config-type:                The input config based on input type:  amber, charmm36, etc."
    echo "  output-directory:           Path to place all of the output."
    echo "  quick:                      [Optional] Tells the program to use the config files in the short-debug-tests directories instead."
    exit 2
fi

cMD_Directory=`realpath $1`
config_type=$2
OUTPUT_BASE=$3
quick=$4

mkdir "$OUTPUT_BASE"

for boost_type in "${boost_types[@]}"
do
    echo "Now running boost type: $boost_type"
    echo "-----------------------------------------------------------"
    ./scripts/do-average-test.sh $cMD_Directory $config_type $boost_type $OUTPUT_BASE/test-$boost_type/ $quick
    mv $OUTPUT_BASE/test-$boost_type/*.png $OUTPUT_BASE/
    echo "-----------------------------------------------------------"
    
done

echo "All Simulations complete."
