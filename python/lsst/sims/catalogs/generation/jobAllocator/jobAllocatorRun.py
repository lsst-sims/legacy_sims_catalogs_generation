import os, sys, cPickle
import jobAllocatorStubs
from lsst.sims.catalogs.generation.db import jobDB as jobDB

if __name__ == '__main__':
    jobId = int(sys.argv[1])
    d = jobDB.JobState(jobId)
    procId = sys.argv[2]
    pickleFile = sys.argv[3]
    d.updateState(procId, 'jARRunning')
    print 'JAR: State %i %s %s' % (
        d._jobid, procId, d.queryState(procId))
    print 'Started job: %i %s %s' % (
        jobId, procId, sys.argv[3])

    t0 = '%s: ' % (procId)
    print t0, 'Unpickling...'
    instanceCat = cPickle.load(open(pickleFile))
    dataFile = instanceCat.jobAllocatorDataFile
    catalogType = instanceCat.jobAllocatorCatalogType

    print t0, 'makeHelio...'
    instanceCat.makeHelio()
    print t0, 'makeTrimCoords...'
    instanceCat.makeTrimCoords()
    print t0, 'validateData...'
    instanceCat.validateData(catalogType)
    print t0, 'writeCatalogData... %s %s' % (dataFile, catalogType)
    instanceCat.writeCatalogData(dataFile, catalogType)

