import os, sys, cPickle
import jobAllocatorStubs
from lsst.sims.catalogs.generation.db import jobDB as jobDB

if __name__ == '__main__':
    print 'Started.'
    jobId = int(sys.argv[1])
    d = jobDB.JobState(jobId)
    procId = sys.argv[2]
    pickleFile = sys.argv[3]
    d.updateState(procId, 'jARRunning')
    print 'JAR: State %i %s %s' % (
        d._jobid, procId, d.queryState(procId))
    print 'Started job: %i %s %s' % (
        jobId, procId, sys.argv[3])

    jobIdStr = '%s: ' % (procId)
    print jobIdStr, 'Unpickling...'
    instanceCat = cPickle.load(open(pickleFile))
    dataFile = instanceCat.jobAllocatorDataFile
    catalogType = instanceCat.jobAllocatorCatalogType

    print jobIdStr, 'makeHelio...'
    instanceCat.makeHelio()
    print jobIdStr, 'makeTrimCoords...'
    instanceCat.makeTrimCoords()
    print jobIdStr, 'validateData...'
    instanceCat.validateData(catalogType)
    print jobIdStr, 'writeCatalogData... %s %s' % (dataFile, catalogType)
    instanceCat.writeCatalogData(dataFile, catalogType)

    # Don't move the file; I want to find it and cat it to a trim file
    #t0 = 'mv %s /share/sdata1/rgibson/catOut/' % dataFile
    #print t0
    #os.system(t0)
    d.updateState(procId, 'JAFinished')
