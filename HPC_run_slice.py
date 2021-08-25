""" HPC_run_slice.py
Build the pbs script for running a single fish 

"""
from subprocess import call
import sys
import glob
import os


if len(sys.argv) != 4:
    print("Missing required arguments. Should be <slice_folder> <output_folder> <fps>")
    print("Example: python HPC_run_slice.py /QRISdata/Q2396/SPIM120170/Spontaneous/slice0 /QRISdata/Q4008/zfish_s2p_slice_output/ 2")
    exit()
print("Args:", sys.argv)

slice_folder = os.path.normpath(sys.argv[1])
output_folder = os.path.normpath(sys.argv[2])
fps = sys.argv[3]

## Define variables needed for file
users_school = 'UQ-EAIT-ITEE' # likely UQ-QBI or UQ-SCI-SBMS

## Build pbs script 
file_contents = f"""#!/bin/bash
#PBS -N s2p_slice
#PBS -A {users_school}
#PBS -l select=1:ncpus=12:mem=110GB:vmem=110GB
#PBS -l walltime=12:00:00
#PBS -j oe
#PBS -k doe


module load anaconda
source activate suite2p

for fish_tif in `ls {slice_folder}/*.tif`; do
    /usr/local/bin/recall_medici $fish_tif
done

python ~/pipelina/run_fish.py {slice_folder} {output_folder} {fps}
"""


## Write pbs script to disk
pbs_filename = 'HPC_run_slice.pbs'
with open(pbs_filename, 'w') as fp:
    fp.write(file_contents)


## Launch the HPC job
job_string = f"qsub {pbs_filename}"
print(job_string)
call([job_string],shell=True)