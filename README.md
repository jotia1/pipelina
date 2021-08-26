# pipelina
Pipelina is a pipeline for automating as many steps as possible in processing calcium imaging data. It provides tools to launch and then manage jobs on the Awoonga compute cluster. A key feature of Pipelina is the ability to restart jobs that have failed due to spurious reasons such as the data storage temporarily dropping out. In particular Pipelina processes raw calcium imaging data and provides biologically releveant signals and analyses. 

# External server
The restarting functionality of Pipelina is provided by the zfishcommand.py file which should be run on a server seperate to the computing cluster. Originally this server was the a zone provided by the Faculty of EAIT, see https://help.eait.uq.edu.au/smartos/ 
Example command to start zfishcommand: 
nohup python3 zfishcommand.py /QRISdata/Q4070/SPIM/Raw/Spontaneous/ /QRISdata/Q4008/MECP2/spont/fish8_11 2 fish811spontFull >>fish811spontFull.txt 2>&1 &
Note, this will also keep the command server running after that particular terminal closes. 

The server communicates with the HPC cluster by setting up an SSH connection using paramiko, it then executes varios bash commands on the cluster to launch jobs and monitor the state of jobs. 

# On the HPC
The typical structure on the HPC conists of a HPC_run_{file}.py python file. The python file creates and then submits a pbspro script. 
