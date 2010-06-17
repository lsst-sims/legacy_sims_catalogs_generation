import sys, random, time
from lsst.sims.catalogs.generation.db import jobDB

def howManyJobs(eM, tableId):
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    if t0 == None: t0 = 0
    else: t0 = int(t0)
    print 'howManyJobs: Current num: ', t0
    return t0

def qsubJob(eM, tableId, jobId):
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    if t0 == None: t0 = 0
    print 'addJob: Current num: ', t0
    t1 = int(t0) + 1
    eM.updateState(tableStr + 'NumJobs', str(t1))
    print 'addJob: New num: ', t1
    jobKey = tableId + '_' + jobId + '_JobState'
    eM.updateState(jobKey, 'QSUBBED')
    eM.updateState(jobKey + 'qsubTime', time.ctime())
    eM.showStates()

def jobRunning(eM, tableId, jobId):
    jobKey = tableId + '_' + jobId + '_JobState'
    eM.updateState(jobKey, 'RUNNING')
    eM.updateState(jobKey + 'RunningTime', time.ctime())
    eM.showStates()

def jobFinished(eM, tableId, jobId):
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    print 'addJob: Current num: ', t0
    t1 = int(t0) - 1
    eM.updateState(tableStr + 'NumJobs', str(t1))
    print 'addJob: New num: ', t1
    jobKey = tableId + '_' + jobId + '_JobState'
    eM.updateState(jobKey, 'FINISHED')
    eM.updateState(jobKey + 'finishedTime', time.ctime())
    eM.showStates()

    
def throttle(eM, tableId, maxNumJobs, throttleTime):
    print 'throttle: maxNumJobs is ', maxNumJobs
    done = False
    while done == False:
        numJobs = howManyJobs(eM, tableId)
        print 'throttle: numJobs is ', numJobs
        if numJobs >= maxNumJobs:
            print 'Max reached; sleeping...'
            time.sleep(throttleTime)
            print 'Waking to check again.'
        else:
            done = True


tableId = sys.argv[1]
print 'Using tableId: ', tableId
eM = jobDB.JobState(tableId)

for i in range(10):
    jobId = 'Job' + str(i)
    print '%i:  Current num jobs'
    howManyJobs(eM, tableId)
    print '--------'
    throttle(eM, tableId, 5, 10)
    print '%s: qsubbing Job (for pretend)' % jobId
    qsubJob(eM, tableId, jobId)
    print '%s: Job running (for pretend)' % jobId
    jobRunning(eM, tableId, jobId)
    print '%s: Job finished (for pretend)' % jobId
    jobFinished(eM, tableId, jobId)
    print '--------'

print 'The final state of the table:'
eM.showStates()
