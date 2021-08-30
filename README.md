# pipelina
Pipelina is a pipeline for automating as many steps as possible in processing calcium imaging data. It provides tools to launch and then manage jobs on the Awoonga compute cluster. A key feature of Pipelina is the ability to restart jobs that have failed due to spurious reasons such as the data storage temporarily dropping out. In particular Pipelina processes raw calcium imaging data and provides biologically releveant signals and analyses. 

# How do I process my data?

## Get Josh to add you the command server
The pipeline is controlled by an external server (the command server) which launches jobs on Awoonga and periodically checks on them. To access the server you will need to be added, give your uq staff id (or student number) to Josh who will add you.

## Set up pipelina on Awoonga
Now we will need to set up pipelina on Awoonga. First log into Awoonga using PuTTY, into the field asking for Host name type the address:
```
awoonga.qriscloud.org.au
```
Log in using the **same** UQ user account that you will use for the command server (that is, don't mix your staff and student accounts if you have both). Now we will need to make sure pipelina know who you are, copy this command into the PuTTY window and replace "your-user-name" with your UQ user name.
```
echo "export UQUSERNAME=your-user-name" >> ~/.bashrc
```

QRIS also requires we tell them which school we belong to at UQ, this varies between different lab members but is likely going to be `UQ-EAIT-ITEE`, `UQ-QBI` or `UQ-SCI-SBMS`. Replace "your-uq-school" with whichever is appropriate for you. If you are unsure which account is correct for you ask Josh.
```
echo "export UQSCHOOL=your-uq-school" >> ~/.bashrc
```
And now lets make sure those are used correctly, again copying this line into the PuTTY window
```
source ~/.bashrc
```
Check these are correct using 
```
echo $UQUSERNAME
echo $UQSCHOOL
```
These should print your correct username and school string.

### Install miniconda
**NOTE**: Skip miniconda installation for now, instead just try `module load anaconda` # TODO : Check what is best for conda on awoonga.
Anaconda is helpful for managing Python enviroments and packages, we will install Miniconda which is a barebones version. While still logged into Awoonga over ssh (through PuTTY) enter the following commands one by one, when prompted agree to the terms, conditions and installation location:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
rm Miniconda3-latest-Linux-x86_64.sh
```

### Install Suite2p
We will need to download the code for [Suite2p](https://github.com/MouseLand/suite2p), but first we will make sure we are in the home directory, enter the following commands into the PuTTY window
```
cd ~/
git clone https://github.com/MouseLand/suite2p.git
```
Now lets go into the Suite2p folder and actually set up the Anaconda environment
```
cd suite2p
conda env create -f environment.yml
```
To Activate and use the suite2p environment you can use the command
```
conda activate suite2p
```

### Download pipelina
To install pipelina on Awoonga we will first need to go back to the home directory and then download pipelinas code
```
cd ~/
git clone git@github.com:jotia1/pipelina.git
```

## Set up pipelina on command server
Now that pipelina is install on Awoonga we will also need to install it on the command server. Start a new PuTTY window to connect to the command server. Once Josh has added you you will be able to log into the server using ssh (through PuTTY) as you would normally access Awoonga. The servers host name is:
```
uqjarno4-zfish.zones.eait.uq.edu.au
```

If this is your first time logging into the command server you will need to set up pipelina, run the following command to download pipelina
```
git clone https://github.com/jotia1/pipelina.git
```

Now make sure pipelina knows which user account to use when it tries to connect to awoonga, in the following command replace "your-user-name" with your UQ user name
```
echo "export UQUSERNAME=your-user-name" >> ~/.bashrc
source ~/.bashrc
```

### Set up SSH keys between command server and Awoonga
To allow the command server to access Awoonga without you there to enter your password we need to set up a pair of keys ([more info](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)). First we will need to generate some keys for your account on the command server, use the default install location with no pass phrase.
```
ssh-keygen -t ed25519
ssh-copy-id ${UQUSERNAME}@awoonga.qriscloud.org.au
```

## Launch a job
Log into the command server through ssh (using PuTTY), the hostname is (`uqjarno4-zfish.zones.eait.uq.edu.au`) 

Change into the pipelina directory 
```
cd pipelina
```

You will need a few bits of information before you can run pipelina: 
- `JOBNAME="descriptive-name"` - A short descriptive name for the job, can be anything but its important it is unique to any other running jobs e.g. `fish8-11Spont`
- `INPUTFOLDER="/path/to/folder/with/multiple/fish"` - The folder in which the fish folders to process are
- `OUTPUTFOLDER="path/where/s2p/output/should/save"` - The folder in which the finished fish will be saved
- `FPS="2"` - The frame rate used in the recording
- `NPLANES="50"` - The number of planes used
- `GCAMPTYPE="gcamp6f"` - The gcamp version used, must be one of [gcamp6s, gcamp6f]

You can set all of these values in the file called `run_zfishcommand.sh`. To open the file we can use the nano text editor, when you are done you can save by pressng Ctrl+o and then enter. To exit press Ctrl+x.
```
nano run_zfishcommand.sh
```
Once you are sure the details are correct you can launch the job by typing
```
./run_zfishcommand.sh
```
The program will start running in the background, if you check the `qstat` command on Awoonga you will soon see jobs starting.


## Checking on a job or debugging
To check if a zfishcommand program is running you can use the command 
```
ps ux | grep zfishcommand
```
To check the logs (which tell us what the program is doing / did) we need to know the jobname specified for the job. We can then view the logs using
```
cat descriptive-name.log
``` 
which will just paste the whole log to the screen, alternatively you could use `nano` to open the file directly or filezilla to copy the log onto your own local computer and then open it with any text editor.



## Additional information about pipelina

# External server
The restarting functionality of Pipelina is provided by the zfishcommand.py file which should be run on a server seperate to the computing cluster. Originally this server was the a zone provided by the Faculty of EAIT, see [https://help.eait.uq.edu.au/smartos/](https://help.eait.uq.edu.au/smartos/)
Example command to start zfishcommand: 
nohup python3 zfishcommand.py /QRISdata/Q4070/SPIM/Raw/Spontaneous/ /QRISdata/Q4008/MECP2/spont/fish8_11 2 fish811spontFull >>fish811spontFull.txt 2>&1 &
Note, this will also keep the command server running after that particular terminal closes. 

The server communicates with the HPC cluster by setting up an SSH connection using paramiko, it then executes varios bash commands on the cluster to launch jobs and monitor the state of jobs. 

# On the HPC
The typical structure on the HPC conists of a HPC_run_{file}.py python file. The python file creates and then submits a pbspro script. 
