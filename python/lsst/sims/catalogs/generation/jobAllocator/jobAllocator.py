import os, sys, time, cPickle
from jobAllocatorStubs import *
import getFileNameWC
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.generation.db import jobDB

class JobAllocator:

    nJobs = None
    catalogTypes = None
    chunkSize = None

    metaDataManager = None
    catalogTypeManager = None
    uIToDBManager = None
    DBManager = None
    executionDBManager = None

    # I don't remember what these are for...
    chunkOutputs = None #???
    fileName = None #???
    directory = None #???
    
    def __init__(self, workDir='/local/tmp/jobAllocator/', chunkSize=1000):
        self.nJobs = None
        self.catalogTypes = None
        self.chunkSize = None
        self.metaDataManager = MetaDataManager()
        self.catalogTypeManager = CatalogTypeManager()
        self.uIToDBManager = UIToDBManager()
        self.DBManager = queryDB.queryDB(chunksize=chunkSize)
        self.executionDBManager = jobDB.JobState()
        if not os.path.exists(workDir):
            os.system('mkdir %s' % workDir)
        self.WorkDir = workDir.rstrip('/') + '/'
        self.nextFileNum = 0
        
    def reset(self):
        self.nJobs = None
        self.catalogTypes = None
        self.chunkSize = None
        if self.metaDataManager:
            self.metaDataManager.reset()
        if self.catalogTypeManager:
            self.catalogTypeManager.reset()
        if self.uIToDBManager:
            self.uIToDBManager.reset()
        #if self.DBManager:
        #    self.DBManager.reset()
        #if self.executionDBManager:
        #    self.executionDBManager.reset()
        self.WorkDir = None
        self.nextFileNum = 0

    def clearMetaData(self):
        """Flush the current metaData."""
        self.metaDataManager.reset()

    def addMetaDataFromFiles(metaDataFileList):
        """Merge metaData from files in the list into the current set
        of metaData.  This is a bit vague right now; how it works depends
        on the metaData classes."""
        for m in metaDataFileList:
            self.metaDataManager.mergeFromFile(m)
    
    def addMetaData(self, metaData):
        self.metaDataManager.merge(metaData)

    def verifyMetaData():
        """For each registered catalog type, check that appropriate
        data is present.  Then call lower-level metaData verify()."""
        for c in catalogTypes:
            self.catalogTypeManager.verifyMetaData(c, self.metaDataManager)

    def getNextGoodFileNum(self):
        nTry = 0
        while len(getFileNameWC.do(self.WorkDir, '*%i*.ja' % self.nextFileNum)) > 0:
            self.nextFileNum += 1
            nTry += 1
            if nTry > 10000:
                raise RuntimeError, '*** Could not find a unique file number.'
        return self.nextFileNum

    def startCatalogs(self, catalogTypes, query, obsHistID):
        #nFN = self.getNextGoodFileNum()
        nFN = self.executionDBManager.getJobId()
        print 'Using job ID: %i' % nFN
        jobNum = 0
        jobTypes = []; jobNums = []; jobPickleFiles = []; useTypes = []
        self.metaDataManager.reset()
        print 'Querying DB for first chunk.'
        instanceCat = self.DBManager.getInstanceCatalogById(obsHistID)
        print 'Got first chunk.'
        # RRG:  Hack; have Simon incorporate
        curMD = None
        numCats = 0; maxCats = 100
        while instanceCat:
            # RRG:  Hack; have Simon incorporate
            instanceCat.objectType = 'POINT'
            if curMD == None: curMD = instanceCat.metadata
            else:
                curMD.mergeMetadata(instanceCat.metadata)
            t0 = self.WorkDir + 'catData%i_%i.ja' % (nFN, jobNum)
            t1 = self.WorkDir + 'catData%i_%i.p' % (nFN, jobNum)
            for t in catalogTypes:
                if t not in useTypes: useTypes.append(t)
                print 'Now pickling catalog type: %s' % t
                # Store job data files in instance
                instanceCat.jobAllocatorDataFile = t0
                instanceCat.jobAllocatorCatalogType = t
                cPickle.dump(instanceCat, open(t1, 'w'))
                jobTypes.append(t)
                jobNums.append(jobNum)
                jobPickleFiles.append(t1)
                jobNum += 1
            #instanceCat = None
            print 'Querying DB for next chunk.'
            instanceCat = self.DBManager.getNextChunk()
            print 'Got next chunk or end.'
            numCats += 1
            if numCats >= maxCats: break
        for t in useTypes:
            curMD.validateMetadata(t)
            mFName = self.WorkDir + 'metaData%i_%s.ja' % (nFN, t)
            curMD.writeMetadata(mFName, t)
        
        # Now fire off the jobs
        for i in range(len(jobNums)):
            jobId = '%i_%i' % (nFN, jobNums[i])
            self.executionDBManager.updateState(jobId, 'JAAdded')
            print 'Added job: %s' % jobId
            #t0 = '/astro/apps/pkg/python64/bin/python jobAllocatorRun.py %i %s %s&' % (nFN, jobId, jobPickleFiles[i])
            #t0 = 'qsub ./runOneAthena.csh %i %s %s&' % (nFN, jobId, jobPickleFiles[i])
            #t0 = 'ssh athena0 "(cd $PBS_O_WORKDIR; qsub ./runOneAthena.csh %i %s %s)"' % (nFN, jobId, jobPickleFiles[i])
            f0 = open('tmpJA%s.csh' % jobId, 'w')
	    f0.write('#!/bin/csh\n#PBS -N jA%s\n#PBS -l walltime=1:00:00\n#PBS -e jA%s.err\n#PBS -o jA%s.out\ncd /share/home/rgibson/sims/catalogs/generation/trunk/python/lsst/sims/catalogs/generation/jobAllocator\nsource setupAthena.csh\npython jobAllocatorRun.py %i %s %s\necho Finished.' % (jobId, jobId, jobId, nFN, jobId, jobPickleFiles[i]))
            f0.close()
            t0 = 'ssh athena0 "(cd /share/home/rgibson/sims/catalogs/generation/trunk/python/lsst/sims/catalogs/generation/jobAllocator; qsub tmpJA%s.csh)"' % (jobId)
            print t0
            os.system(t0)

        # Check that everything started within a certain time limit
        # On athena, jobs may be queued indefinitely, so this won't work
        for i in range(len(jobNums)):
            jobId = '%i_%i' % (nFN, jobNums[i])
            tryNum = 0
            t0 = self.executionDBManager.queryState(jobId)
            while t0 != 'JAFinished':
                print 'JA sees state for %s: %s' % (jobId, t0)
                time.sleep(1)
                if tryNum > 3000:
                    raise RuntimeError, '*** Job not started: %s' % jobId
                tryNum += 1
                t0 = self.executionDBManager.queryState(jobId)
            print 'JA sees state for %s: %s' % (jobId, t0)

    # Private
    def _setnJobs(self, nJobs):
        """Verify value and then assign it."""
        verifynJobs(nJobs)
        self.nJobs = nJobs
        
    def _setcatalogTypes(self, catalogTypes):
        """Verify value and then assign it."""
        verifycatalogTypes(catalogTypes)
        self.catalogTypes = catalogTypes
        
    def _setchunkSize(self, chunkSize):
        """Verify value and then assign it."""
        verifychunkSize(chunkSize)
        self.chunkSize = chunkSize

    def _verifynJobs(nJobs):
        """If value is not appropriate, raise a ValueError exception."""

    def _verifycatalogTypes(catalogTypes):
        """If value is not appropriate, raise a ValueError exception."""

    def _verifychunkSize(chunkSize):
        """If value is not appropriate, raise a ValueError exception."""

        




#Controller -> JobAllocator: clear()
#Controller -> JobAllocator: addMetaDataList(metaDataFileList)
#JobAllocator -> MetaDataManager: load(metaDataFile0)
#MetaDataManager -> JobAllocator: data
#JobAllocator -> MetaDataManager: load(metaDataFileN)
#MetaDataManager -> JobAllocator: data
#JobAllocator -> MetaDataManager: mergeMetaDataList(metaDataList)
#MetaDataManager -> JobAllocator: Done
#JobAllocator -> MetaDataManager: verifyMetaData(metaDataList)
#JobAllocator -> Controller: Done
#Controller -> JobAllocator: makeCatalogs(catalogTypes, uIInfo, chunkSize=None, nJobs=None)
#JobAllocator -> CatalogTypeManager: verifyMetaData(catalogTypes, metaData)
#CatalogTypeManager -> JobAllocator: Done
#JobAllocator -> JobAllocator: writeMetaDataFile(outFile)
#JobAllocator -> UIToDBManager: constructDBQuery(uIInfo)
#UIToDBManager -> JobAllocator: dBQuery
#JobAllocator -> DBQuery: initialize(dBQuery, chunkSize)
#JobAllocator -> DBQuery: queryNextChunk()
#DBQuery -> JobAllocator: dBChunk
#JobAllocator -> InstanceCatalog: instantiate(catalogTypes, metaDataFile, dBChunk)
#InstanceCatalog -> CatalogTypeManager: verifyMetaData(catalogTypes, metaData)
#CatalogTypeManager -> InstanceCatalog: Done
#InstanceCatalog -> JobAllocator: jobParameters
#JobAllocator -> ExecutionDB: newJob(jobParameters)
#ExecutionDB -> JobAllocator: Done
#JobAllocator -> Controller: Done(executionDBTable)
