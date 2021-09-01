#! /bin/bash

JOBNAME="pplna_2396"
INPUTFOLDER="/QRISdata/Q2396/SPIM_120170/Spontaneous"
OUTPUTFOLDER="/QRISdata/Q4008/Q2396/Spontaneous"
JOBTYPE='fish-whole'
S2PCONFIG='ops_1P_whole.json'
# This job will be the first actual s2p tests of the new pipelina model

echo "------------------------------------------" >>${JOBNAME}.txt
date >>${JOBNAME}.txt
cat ${0##*/} >>${JOBNAME}.txt  # copy this file into jobname.txt
echo "" >>${JOBNAME}.txt

nohup python3 pipelina.py -j $JOBTYPE -i $INPUTFOLDER -o $OUTPUTFOLDER -s $S2PCONFIG  ${JOBNAME} >>${JOBNAME}.txt 2>&1 &
