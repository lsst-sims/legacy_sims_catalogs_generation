import sys, random, time
from lsst.sims.catalogs.generation.db import jobDB

def howManyJobs(eM, tableId, jobInt):
    tableStr = str(tableId)
    eM = jobDB.JobState(jobInt)
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    if t0 == None: t0 = 0
    else: t0 = int(t0)
    print 'howManyJobs: Current num: ', t0
    return t0

def qsubJob(tableId, jobId, jobName):
    tableStr = str(tableId)
    eM = jobDB.JobState(tableId)
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    if t0 == None: t0 = 0
    print 'addJob: Current num: ', t0
    t1 = int(t0) + 1
    eM.updateState(tableStr + 'NumJobs', str(t1))
    print 'addJob: New num: ', t1
    jobKey = tableId + '_%s' %(jobId) + 'JS'
    eM.updateState(jobKey, 'QSUBBED')
    eM.updateState(jobKey + 'QT', time.ctime())
    jobKeyN = tableId + '_%s' %(jobId) + 'N'
    eM.updateState(jobKeyN, jobName)
    eM.showStates()

def jobRunning(eM, tableId, jobId):
    tableStr = str(tableId)
    jobKey = tableId + '_%s' %(jobId) + 'JS'
    eM.updateState(jobKey, 'RUNNING')
    eM.updateState(jobKey + 'RT', time.ctime())
    eM.showStates()

def jobFinished(eM, tableId, jobId):
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    print 'addJob: Current num: ', t0
    t1 = int(t0) - 1
    eM.updateState(tableStr + 'NumJobs', str(t1))
    print 'addJob: New num: ', t1
    jobKey = tableId + '_%s' %(jobId) + 'JS'
    eM.updateState(jobKey, 'FINISHED')
    eM.updateState(jobKey + 'FT', time.ctime())
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

if not len(sys.argv) == 4:
    print "usage: %python myJobMonitor.py tableId state jobId"
    quit()
    
tableId = sys.argv[1]
state = sys.argv[2]
jobId = sys.argv[3]


## Example Test
## for i in range(10):
##     jobId = 'Job' + str(i)
##     print '%i:  Current num jobs' % i
##     howManyJobs(eM, tableId)
##     print '--------'
##     print '%s: qsubbing Job (for pretend)' % jobId
##     qsubJob(eM, tableId, jobId, 'MyJobNameForJob%i' % i)
##     print '%s: Job running (for pretend)' % jobId
##     jobRunning(eM, tableId, jobId)
##     print '%s: Job finished (for pretend)' % jobId
##     jobFinished(eM, tableId, jobId)
##     print '--------'

## print 'The final state of the table:'
## eM.showStates()

if state == 'running':
    tableStr = str(tableId)
    #eM = jobDB.JobState(tableId)
    jobInt = int(jobId)
    eM = jobDB.JobState(jobInt)
    #jobRunning(eM, tableId, jobId)
    jobRunning(eM, tableStr, jobId)

if state == 'finished':
    tableStr = str(tableId)
    jobInt = int(jobId)
    eM = jobDB.JobState(jobInt)
    jobFinished(eM, tableStr, jobId) 

