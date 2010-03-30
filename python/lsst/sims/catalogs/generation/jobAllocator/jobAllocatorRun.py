import os, sys
import jobAllocatorStubs
from lsst.sims.generation.db import jobDB as jobDB

if __name__ == '__main__':
    jobId = int(sys.argv[1])
    d = jobDB.JobState(jobId)
    procId = sys.argv[2]
    d.updateState(procId, 'jARRunning')
    print 'JAR: State %i %s %s' % (
        d._jobid, procId, d.queryState(procId))
    print 'Started job: %i %s %s %s' % (
        jobId, procId, sys.argv[3], sys.argv[4])
