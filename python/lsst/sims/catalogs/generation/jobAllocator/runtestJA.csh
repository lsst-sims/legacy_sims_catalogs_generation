#!/bin/csh
#PBS -e runJA.err
#PBS -o runJA.out
cd $PBS_O_WORKDIR
echo Setup...
source setupAthena.csh
echo test_JA...
python test_jobAllocator.py
echo Finished.
