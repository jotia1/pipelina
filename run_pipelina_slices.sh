#! /bin/bash

JOBNAME="splna_2396"
INPUTFOLDER="/QRISdata/Q2396/Preprocessed/Spontaneous/scn1lab_fish_19_25/"
OUTPUTFOLDER="/QRISdata/Q4008/Q2396/sliced/scn1lab_fish_19_25"
JOBTYPE='fish-slices'
S2PCONFIG='ops_1P_slices.json'
# This job will be the first actual s2p tests of the new pipelina model
# WHEN USING SLICES for fish 19-25, note full fish is 5-10

echo "------------------------------------------" >>${JOBNAME}.txt
date >>${JOBNAME}.txt
cat ${0##*/} >>${JOBNAME}.txt  # copy this file into jobname.txt
echo "s2p file:" >>${JOBNAME}.txt
cat $S2PCONFIG >>${JOBNAME}.txt

nohup python3 pipelina.py -j $JOBTYPE -i $INPUTFOLDER -o $OUTPUTFOLDER -s $S2PCONFIG  ${JOBNAME} >>${JOBNAME}.txt 2>&1 &
