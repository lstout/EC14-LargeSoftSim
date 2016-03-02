#!/bin/sh

# arg 1 is the absolute path to the experiment with '/' at the end
# arg 2 is the number of the pool to use. The corresponding pool file has to be found at ${1}pool/vox.${2}.pool

base=${1}
n=$PBS_ARRAYID

pool=dead${n}.pool
population=${base}population/ #have to skip home, because qsub replaces it
traces=${base}traces_
pool_input=${base}pool/vox.${n}.pool
logs=${base}logs

module load stopos
stopos create -p ${pool}
stopos add -p ${pool} ${pool_input}

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/controller/scripts

# 1 hour max runtime... should suffice for a max individual lifetime of approx. 25-30s
JOB_ID=`qsub -o ${logs}/${n}.output.log -e ${logs}/${n}.error.log -l nodes=1,walltime=${3} -v pool=${pool},population=${population},traces=${traces} ${scriptdir}/run_vox.sh`

echo ${JOB_ID}
