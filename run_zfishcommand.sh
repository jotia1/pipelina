#! /bin/bash

JOBNAME="fish811audFull"
INPUTFOLDER="/QRISdata/Q4070/SPIM/Resliced/Auditory/fish8_11"
OUTPUTFOLDER="/QRISdata/Q4008/MECP2/aud/fish8_11"
FPS="2"
NPLANES="50"
GCAMPTYPE="gcamp6f"

date >>${JOBNAME}.txt
cat run_zfishcommand.sh >>${JOBNAME}.txt

nohup python3 zfishcommand.py $INPUTFOLDER $OUTPUTFOLDER $FPS $NPLANES $GCAMPTYPE >>${JOBNAME}.txt 2>&1 &
