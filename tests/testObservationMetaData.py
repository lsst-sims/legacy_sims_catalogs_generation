import os
import unittest
import lsst.utils.tests as utilsTests
from collections import OrderedDict
from lsst.sims.catalogs.generation.db import ObservationMetaData

class ObservationMetaDataTest(unittest.TestCase):
    """
    This class will test that ObservationMetaData correctly assigns
    and returns its class variables (UnrefractedRA, UnrefractedDec, etc.)
    """
    
    def testDefault(self):
        testObsMD = ObservationMetaData()
        
        self.assertAlmostEqual(testObsMD.UnrefractedRA,0.0,10)
        self.assertAlmostEqual(testObsMD.UnrefractedDec,-0.5,10)
        self.assertAlmostEqual(testObsMD.RotSkyPos,0.0,10)
        self.assertEqual(testObsMD.bandpass,'i')
    
    def testAssignment(self):
        mjd = 5120.0
        RA = 1.5
        Dec = -1.1
        RotSkyPos = -0.2
        
        testObsMD = ObservationMetaData(mjd=mjd, UnrefractedRA=RA,
            UnrefractedDec=Dec, RotSkyPos=RotSkyPos, bandpassName = 'z')
        
        self.assertAlmostEqual(testObsMD.mjd,5120.0,10)
        self.assertAlmostEqual(testObsMD.UnrefractedRA,1.5,10)
        self.assertAlmostEqual(testObsMD.UnrefractedDec,-1.1,10)
        self.assertAlmostEqual(testObsMD.RotSkyPos,-0.2,10)
        self.assertEqual(testObsMD.bandpass,'z')
        
        phosimMD = OrderedDict([('Unrefracted_RA', (-2.0,float)), 
                                ('Unrefracted_Dec', (0.9,float)),
                                ('Opsim_rotskypos', (1.1,float)), 
                                ('Opsim_expmjd',(4000.0,float)),
                                ('Opsim_filter',(1,int))])
        
        testObsMD.assignPhoSimMetaData(phosimMD)
        
        self.assertAlmostEqual(testObsMD.mjd,4000.0,10)
        self.assertAlmostEqual(testObsMD.UnrefractedRA,-2.0,10)
        self.assertAlmostEqual(testObsMD.UnrefractedDec,0.9,10)
        self.assertAlmostEqual(testObsMD.RotSkyPos,1.1,10)
        self.assertEqual(testObsMD.bandpass,'g')

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
