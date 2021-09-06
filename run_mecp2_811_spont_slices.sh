#! /bin/bash

JOBNAME="mecp2-811-spont-slices"
INPUTFOLDER="/QRISdata/Q4070/SPIM/Resliced/Spontaneous/fish8_11"
OUTPUTFOLDER="/QRISdata/Q4008/s2p_slices/spont/fish8_11"
JOBTYPE='fish-slices'
S2PCONFIG='ops_1P_slices.json'

# Restart mecp2 as pipelina run

echo "------------------------------------------" >>${JOBNAME}.txt
date >>${JOBNAME}.txt
cat ${0##*/} >>${JOBNAME}.txt  # copy this file into jobname.txt
echo "s2p file:" >>${JOBNAME}.txt
cat $S2PCONFIG >>${JOBNAME}.txt

nohup python3 pipelina.py -j $JOBTYPE -i $INPUTFOLDER -o $OUTPUTFOLDER -s $S2PCONFIG  ${JOBNAME} >>${JOBNAME}.txt 2>&1 &
