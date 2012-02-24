# execfile('testThrottleObsList.py')

import os, sys, time
from lsst.sims.catalogs.generation.db import jobDB
import throttleUtils

maxNumJobs = 100
waitTime = 5

radDeg = 2.1
#obsList = [
#    '88533589', '88544863', '88545027', '88572282', '88572405',
#    '88625722', '88625768', '88625873', '88626439', '88646885',
#    '88646916', '88646953', '88646972', '88673409', '88673551',
#    '88687053', '88689380', '88689479', '88691372', '88691519',
#    '88691756', '88691823', '88702909', '88702909', '88725297',
#    '88725438', '88730520', '88747522', '88747566', '88747628',
#    '88747751', '88767581', '88775449', '88775554', '88775587',
#    '88808278'
#]

#obsList = ['88533589']
obsList = []
f = open('inList.txt', 'r')
for line in f:
    t0 = line.split()
    if len(t0) != 1: continue
    obsList.append(t0[0])

f.close()
print 'obsList:', obsList

numJobs = len(obsList)

executionDBManager = jobDB.JobState()
t0 = executionDBManager.getJobId()

nFN = '%s_%s' % (t0.getOwner(), t0.getId())
print 'Using job ID: %s' % nFN


for i in range(len(obsList)):
    jobId = '%s_%i' % (nFN, i)
    throttleUtils.throttle(executionDBManager, maxNumJobs, waitTime)
    # For now, call addJob() before actually starting the job,
    #  because there could be a race condition if addJob()
    #  and removeJob() are called simultaneously.
    throttleUtils.addJob(executionDBManager, jobId, obsList[i])

    #jobIdPlusI = jobId + '_' + str(i)
    cwd0 = os.getcwd()
    f0 = open('/share/pogo3/rgibson/testFramework011312/sTScripts/tempST%s.csh' % jobId, 'w')
    f0.write('#!/bin/csh\n#PBS -N %i_sT%s\n#PBS -l walltime=23:59:59\n#PBS -e /share/pogo3/rgibson/testFramework011312/out/sT%s.err\n#PBS -o /share/pogo3/rgibson/testFramework011312/out/sT%s.out\n\ncd %s\nsource setupOldAthena.csh\npython ./testThrottleObsListRun.py %s %s %s %s\necho Finished.' % (i, jobId, jobId, jobId, cwd0, nFN, jobId, obsList[i], str(radDeg)))
    f0.close()
    # Use this from a compute node
    t0 = 'ssh minerva0 "(cd %s; /opt/torque/bin/qsub ./sTScripts/tempST%s.csh)"' % (cwd0, jobId)
    #t0 = '/opt/torque/bin/qsub ./sTScripts/tempST%s.csh' % (jobId)
    print t0
    os.system(t0)

print 'Quitting, as all jobs have at least been submitted.  State:'
throttleUtils.showStates(executionDBManager)
