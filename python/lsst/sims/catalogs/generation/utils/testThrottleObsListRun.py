# execfile('testThrottleObsListRun.py')

import os, sys, time, random
from lsst.sims.catalogs.generation.db import jobDB
import throttleUtils

if __name__ == '__main__':
    print 'Started with arg:', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    t0 = sys.argv[1].split('_')
    jobId = jobDB.JobId(int(t0[1]), owner=t0[0])
    d = jobDB.JobState(jobId)
    procId = sys.argv[2]
    obsId = sys.argv[3]
    rad = sys.argv[4]
    d.updateState(procId, 'JobRunning_%s' % (obsId))
    print 'Update state: %s to JobRunning_%s' % (procId, obsId)
    t0 = 'python ./generation/branches/mssql/bin/runFiles.py %s %s'
    t1 = t0 % (obsId, rad)
    succeeded = False
    nAttempsRemaining = 10
    rc = -1
    while succeeded == False and nAttempsRemaining > 0:
        print t1
        rc = os.system(t1)
        if (rc >> 8) == 0:
            d.updateState(procId, 'JAFinished_%s' % (obsId))
            print 'Updated state: %s to JAFinished_%s' % (procId, obsId)
            succeeded = True
        else:
            d.updateState(procId, 'JobRetry_%s' % (obsId))
            print 'Updated state: %s to JobRetry_%s' % (procId, obsId)
            nAttempsRemaining -= 1
            # Sleep a while before restarting in case DB is swamped
            t2 = random.random() * 20 + 10
            time.sleep(t2*60)

    if succeeded == True:
        throttleUtils.removeFinishedJob(d, procId, obsId)
    else:
        throttleUtils.removeFailedJob(d, procId, obsId)
        
    throttleUtils.showStates(d)
