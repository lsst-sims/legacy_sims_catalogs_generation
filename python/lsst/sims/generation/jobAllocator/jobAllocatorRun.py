import os, sys
import jobAllocatorStubs

if __name__ == '__main__':
    d = jobAllocatorStubs.ExecutionDBInterface()
    jobId = sys.argv[1]
    d.startNewJob(jobId)
    print 'Started job: %s %s %s' % (sys.argv[1], sys.argv[2], sys.argv[3])
