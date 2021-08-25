""" HPC_run_fish.py
Build the pbs script for running a single fish 

"""
from subprocess import call
import sys
import glob
import os


if len(sys.argv) != 4:
    print("Missing required arguments. Should be <fish_folder> <output_folder> <fps>")
    print("Example: python HPC_run_fish.py /QRISdata/Q2396/SPIM120170/Spontaneous /QRISdata/Q4008/zfish_s2p_output/ 2")
    exit()
print("Args:", sys.argv)

fish_folder = os.path.normpath(sys.argv[1])
output_folder = os.path.normpath(sys.argv[2])
fps = sys.argv[3]

## Define variables needed for file
users_school = 'UQ-EAIT-ITEE' # likely UQ-QBI or UQ-SCI-SBMS

## Build pbs script 
file_contents = f"""#!/bin/bash
#PBS -N s2p_fish
#PBS -A {users_school}
#PBS -l select=1:ncpus=12:mem=110GB:vmem=110GB
#PBS -l walltime=24:00:00
#PBS -j oe
#PBS -k doe
#PBS -m abe
#PBS -M uqjarno4@uq.edu.au


module load anaconda
source activate suite2p

for fish_tif in `ls {fish_folder}/*.tif`; do
    /usr/local/bin/recall_medici $fish_tif
done

python ~/pipelina/run_fish.py {fish_folder} {output_folder} {fps}
"""


## Write pbs script to disk
pbs_filename = 'HPC_run_fish.pbs'
with open(pbs_filename, 'w') as fp:
    fp.write(file_contents)


## Launch the HPC job
job_string = f"qsub {pbs_filename}"
print(job_string)
call([job_string],shell=True)