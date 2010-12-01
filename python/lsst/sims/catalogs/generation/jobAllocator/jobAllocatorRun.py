import os, sys, cPickle, time
import jobAllocatorStubs
from lsst.sims.catalogs.generation.db import jobDB as jobDB

if __name__ == '__main__':
    print 'Started with arg:', sys.argv[1], sys.argv[2], sys.argv[3]
    t0 = sys.argv[1].split('_')
    jobId = jobDB.JobId(int(t0[1]), owner=t0[0])
    d = jobDB.JobState(jobId)
    procId = sys.argv[2]
    pickleFile = sys.argv[3]
    t0 = time.time()
    d.updateState(procId, 'jARRunning')
    print 'Update to JARunning: %i' % (time.time() - t0)
    print 'JAR: State %s %s' % (
        procId, d.queryState(procId))
    print 'Started job: %s %s' % (
        procId, sys.argv[3])

    jobIdStr = '%s: ' % (procId)
    print jobIdStr, 'Unpickling...'
    t0 = time.time()
    instanceCat = cPickle.load(open(pickleFile))
    print 'pickle load: %i' % (time.time() - t0)

    # Need to work with the catalog type to allow the possibility
    #  of writing out multiple types (loop not implemented yet)
    #  while allowing this code to choose the file names.
    dataFile = instanceCat.jobAllocatorDataFile
    catalogType = instanceCat.jobAllocatorCatalogType

    t0 = time.time()
    print jobIdStr, 'makeHelio...'
    instanceCat.makeHelio()
    print jobIdStr, 'makeTrimCoords...'
    instanceCat.makeTrimCoords()
    print jobIdStr, 'validateData...'
    instanceCat.validateData(catalogType)
    print 'makeHelio, makeTrimCoords, and validateData: %i' % (time.time() - t0)

    print jobIdStr, 'writeCatalogData... %s %s' % (dataFile, catalogType)
    t0 = time.time()
    instanceCat.writeCatalogData(dataFile, catalogType)
    print 'writeCatalogData: %i' % (time.time() - t0)

    # Don't move the file; I want to find it and cat it to a trim file
    #t0 = 'mv %s /share/sdata1/rgibson/catOut/' % dataFile
    #print t0
    #os.system(t0)
    t0 = time.time()
    d.updateState(procId, 'JAFinished')
    print 'Updated state: %s to JAFinished' % procId
    print 'Update to JAFinished: %i' % (time.time() - t0)

