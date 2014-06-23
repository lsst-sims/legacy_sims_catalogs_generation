import os
import unittest
import lsst.utils.tests as utilsTests
from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData
import lsst.sims.catalogs.generation.utils.testUtils as tu

# This test should be expanded to cover more of the framework
# I have filed CATSIM-90 for this.

class DBObjectTestCase(unittest.TestCase):
    def setUp(self):
        #Delete the test database if it exists and start fresh.
        if os.path.exists('testDatabase.db'):
            print "deleting database"
            os.unlink('testDatabase.db')
        tu.makeStarTestDB(size=100000, seedVal=1)
        tu.makeGalTestDB(size=100000, seedVal=1)
        self.obsMd = ObservationMetaData(circ_bounds=dict(ra=210., dec=-60, radius=1.75),
                                         mjd=52000., bandpassName='r')
    def tearDown(self):
        del self.obsMd

    def testObsMD(self):
        self.assertEqual(self.obsMd.bandpass, 'r')
        self.assertAlmostEqual(self.obsMd.mjd, 52000., 6)

    def testDbObj(self):
        mystars = DBObject.from_objid('teststars')
        mygals = DBObject.from_objid('testgals')
        result = mystars.query_columns(obs_metadata=self.obsMd)
        tu.writeResult(result, "/dev/null")
        result = mystars.query_columns(obs_metadata=self.obsMd)
        tu.writeResult(result, "/dev/null")

def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(DBObjectTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)

    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
