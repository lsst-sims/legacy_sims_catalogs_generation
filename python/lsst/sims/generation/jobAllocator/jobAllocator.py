import os, sys, time
from jobAllocatorStubs import *
import getFileNameWC
import lsst.sims.generation.db as db

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
    
    def __init__(self, workDir='/local/tmp/jobAllocator'):
        self.nJobs = None
        self.catalogTypes = None
        self.chunkSize = None
        self.metaDataManager = MetaDataManager()
        self.catalogTypeManager = CatalogTypeManager()
        self.uIToDBManager = UIToDBManager()
        self.DBManager = db.queryDB(chunksize=10)
        self.executionDBManager = ExecutionDBInterface()
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
        if self.executionDBManager:
            self.executionDBManager.reset()
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

    def startCatalogs(self, catalogTypes, query, obsHistID, chunkSize=1000):
        nFN = self.getNextGoodFileNum()
        jobNum = 0
        jobTypes = []; jobNums = []; jobDataFiles = []
        self.metaDataManager.reset()
        instanceCat = self.DBManager.getInstanceCatalogById(obsHistID, filetypes=catalogTypes)
        curMD = instanceCat.metadata
        while instanceCat:
            t0 = self.WorkDir + 'catData%i_%i.ja' % (nFN, jobNum)
            instanceCat.writeCatalogData(t0, catalogTypes)
            jobTypes.append(t)
            jobNums.append(jobNum)
            jobDataFiles.append(t0)
            jobNum += 1
            instanceCat = self.DBManager.getNextChunk()
            curMD.merge(instanceCat.metadata)
        mFName = self.WorkDir + 'metaData%i_%s.ja' % (nFN, t)
        self.metaDataManager.writeToFile(t, mFName)
        
        # Now fire off the jobs
        for i in range(len(jobNums)):
            jobId = '%i_%i' % (nFN, jobNums[i])
            self.executionDBManager.addNewJob(jobId)
            print 'Added job: %s' % jobId
            os.system('python jobAllocatorRun.py %s %s %s &' % (
                jobId, jobTypes[i], jobDataFiles[i]))

        # Check that everything started within a certain time limit
        # On athena, jobs may be queued indefinitely, so this won't work
        for i in range(len(jobNums)):
            jobId = '%i_%i' % (nFN, jobNums[i])
            tryNum = 0
            while not self.executionDBManager.checkJobStarted(jobId):
                time.sleep(1)
                if tryNum > 3:
                    raise RuntimeError, '*** Job not started: %s' % jobId
                tryNum += 1

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
