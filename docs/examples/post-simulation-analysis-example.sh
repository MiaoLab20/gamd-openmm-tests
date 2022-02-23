#!/bin/bash


TEMPERATURE=$1

if [ $# -eq 0 ]
then
  printf "Usage:\n\tpost-simulation-analysis-example.sh temperature\n\n"
  exit 1
fi

mkdir -p analysis/ analysis-out

tail -n +4 gamd-reweighting.log > analysis/headerless-gamd.log
awk 'NR%1==0' analysis/headerless-gamd.log |awk -v TEMP=$TEMPERATURE -v IDEAL_GAS_CONSTANT=0.001987 '{print ($8+$7)/(IDEAL_GAS_CONSTANT*TEMP)" " $2 " " ($8+$7)}' > analysis/weights.dat

cpptraj -p data/dip.prmtop -i psi-dat-commands.cpptraj
awk '{print $2}' analysis/psi-cpptraj.dat |tail -n +2 >psi.dat

cpptraj -p data/dip.prmtop -i phi-dat-commands.cpptraj
awk '{print $2}' analysis/phi-cpptraj.dat |tail -n +2 >phi.dat

cpptraj -p data/dip.prmtop -i phi-psi-commands.cpptraj
awk '{print $2, $3}' analysis/phi-psi-cpptraj.dat |tail -n +2 > phi-psi.dat

PyReweighting-1D.py -input psi.dat -T $TEMPERATURE -cutoff 100 -Xdim -180 180 -disc 6 -Emax 100 -job amdweight_CE -weight analysis/weights.dat | tee -a analysis/reweight-variable-cumulant-expansion-1D.log
mv -v pmf-c1-psi.dat.xvg analysis-out/pmf-psi-reweight-CE1.xvg
mv -v pmf-c2-psi.dat.xvg analysis-out/pmf-psi-reweight-CE2.xvg
mv -v pmf-c3-psi.dat.xvg analysis-out/pmf-psi-reweight-CE3.xvg
mv -v psi.dat analysis/

PyReweighting-1D.py -input phi.dat -T $TEMPERATURE -cutoff 100 -Xdim -180 180 -disc 6 -Emax 100 -job amdweight_CE -weight analysis/weights.dat | tee -a analysis/reweight-variable-cumulant-expansion-1D.log
mv -v pmf-c1-phi.dat.xvg analysis-out/pmf-phi-reweight-CE1.xvg
mv -v pmf-c2-phi.dat.xvg analysis-out/pmf-phi-reweight-CE2.xvg
mv -v pmf-c3-phi.dat.xvg analysis-out/pmf-phi-reweight-CE3.xvg
mv -v phi.dat analysis/

PyReweighting-2D.py -T $TEMPERATURE  -cutoff 100 -input phi-psi.dat -Xdim -180 180 -discX 6 -Ydim -180 180 -discY 6 -Emax 100 -job amdweight_CE -weight analysis/weights.dat | tee -a analysis/reweight-variable-cumulant-expansion-2D.log
mv -v pmf-c1-phi-psi.dat.xvg analysis-out/pmf-2D-phi-psi-reweight-CE1.xvg
mv -v pmf-c2-phi-psi.dat.xvg analysis-out/pmf-2D-phi-psi-reweight-CE2.xvg
mv -v pmf-c3-phi-psi.dat.xvg analysis-out/pmf-2D-phi-psi-reweight-CE3.xvg
mv -v 2D_Free_energy_surface.png analysis-out/pmf-2D-phi-psi-reweight-CE2.png
mv -v phi-psi.dat analysis/

mv -v weights-c1-psi.dat.xvg analysis-out/
mv -v weights-c2-psi.dat.xvg analysis-out/
mv -v weights-c3-psi.dat.xvg analysis-out/
mv -v weights-c1-phi.dat.xvg analysis-out/
mv -v weights-c2-phi.dat.xvg analysis-out/
mv -v weights-c3-phi.dat.xvg analysis-out/
mv -v weights.png analysis-out/weights-psi.png

