import os
import unittest
import lsst.utils.tests as utilsTests
from lsst.sims.catalogs.generation.db import ObservationMetaData

class ObservationMetaDataTest(unittest.TestCase):
    """
    This class will test that ObservationMetaData correctly assigns
    and returns its class variables (UnrefractedRA, UnrefractedDec, etc.)
    """
    
    def testScalars(self):
        mjd = 5120.0
        RA = 1.5
        Dec = -1.1
        RotSkyPos = -0.2
        
        testObsMD = ObservationMetaData(mjd=mjd, UnrefractedRA=RA,
            UnrefractedDec=Dec, RotSkyPos=RotSkyPos)
        
        self.assertAlmostEqual(testObsMD.mjd,5120.0,10)
        self.assertAlmostEqual(testObsMD.UnrefractedRA,1.5,10)
        self.assertAlmostEqual(testObsMD.UnrefractedDec,-1.1,10)
        self.assertAlmostEqual(testObsMD.RotSkyPos,-0.2,10)
        
    

def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(ObservationMetaDataTest)

    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
