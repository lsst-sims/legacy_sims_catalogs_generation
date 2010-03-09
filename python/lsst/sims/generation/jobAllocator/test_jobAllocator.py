import unittest
import jobAllocator

class JobAllocatorTest(unittest.TestCase):
    def testinit(self):
        j = jobAllocator.JobAllocator()
        self.assertEqual(j.nJobs, None)
        self.assertEqual(j.catalogTypes, None)
        self.assertEqual(j.chunkSize, None)
        self.assertNotEqual(j.metaDataManager, None)
        self.assertNotEqual(j.catalogTypeManager, None)
        self.assertNotEqual(j.uIToDBManager, None)

    def testreset(self):
        j = jobAllocator.JobAllocator()
        j.metaDataManager.isCleared = False
        j.catalogTypeManager.isCleared = False
        j.uIToDBManager.isCleared = False
        j.mergedMetaData = -1
        j.nJobs = -1
        j.catalogTypes = -1
        j.chunkSize = -1
        j.reset()
        self.assertEqual(j.nJobs, None)
        self.assertEqual(j.catalogTypes, None)
        self.assertEqual(j.chunkSize, None)
        self.assertNotEqual(j.metaDataManager, None)
        self.assertNotEqual(j.catalogTypeManager, None)
        self.assertNotEqual(j.uIToDBManager, None)
        self.assert_(j.metaDataManager.isCleared)
        self.assert_(j.catalogTypeManager.isCleared)
        self.assert_(j.uIToDBManager.isCleared)

    def testclearMetaData(self):
        j = jobAllocator.JobAllocator()
        j.metaDataManager.isCleared = False
        j.clearMetaData()
        self.assert_(j.metaDataManager)
        self.assert_(j.metaDataManager.isCleared == True)

    def testAddMetaData0(self):
        j = jobAllocator.JobAllocator()
        testDict = { 'a' : 1, 'b' : 2 }
        j.addMetaData(testDict)
        d = j.metaDataManager.dict['main']
        self.assertEqual(len(d.keys()), len(testDict.keys()))
        for k in d.keys():
            self.assertEqual(d[k], testDict[k])
        # Testing beyond this level is up to the MetaData class
        
    def testAddMetaDataN(self):
        j = jobAllocator.JobAllocator()
        n = 100
        for i in range(n):
            j.addMetaData({ str(i) : i })
        d = j.metaDataManager.dict['main']
        self.assertEqual(len(d.keys()), n)
        for i in range(n):
            self.assert_(d.has_key(str(i)))
        # Testing beyond this level is up to the MetaData class

    def teststartCatalogs(self):
        j = jobAllocator.JobAllocator()
        j.startCatalogs(('catType0', 'catType1'), 'TEST QUERY', 'TESTOBSHISTID', 1000)

if __name__ == '__main__':
    unittest.main()
