from lsst.sims.catalogs.generation.db import jobDB

def howManyInQueue(eM, jobId, maxJobs):
    numFinished = 0
    for i in range(maxJobs):
        jobNum = '%i_%' % (jobId, i)
        t0 = eM.queryState(jobNum)
        if t0 == 'Finished': numFinished += 1

    return numFinished


def addJob(eM, tableId):
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    if t0 == None: t0 = 0
    print 'Current num: ', t0
    t1 = int(t0) + 1
    em.updateState(jobKey + 'NumJobs', str(t1))
    print 'New num: ', t1

def removeJob(eM, tableId):
    tableStr = str(tableId)
    t0 = eM.queryState(tableStr + 'NumJobs')
    print 'Current num: ', t0
    t1 = int(t0) - 1
    em.updateState(jobKey + 'NumJobs', str(t1))
    print 'New num: ', t1
    


eM = jobDB.JobState()
nFN = eM.getJobId()
print 'Using jobId: ', nFN

for i in range(10):
    addJob(eM, nFN)
    removeJob(eM, nFN)


