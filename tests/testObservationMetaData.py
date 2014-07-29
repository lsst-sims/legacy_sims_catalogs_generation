import os
import unittest
import lsst.utils.tests as utilsTests
from lsst.sims.catalogs.generation.db import ObservationMetaData


class ObservationMetaDataTestCase(unittest.TestCase):
    def testInit(self):
        m5tuple = (0,1,2,3)
        m5float = 25.
        m5dict = dict(u=25., g=23., r=22.)
        circ_bounds = dict(ra = 25., dec= 50., radius = 5.)
        box_bounds = dict(ra_min = 10., ra_max = 20., 
                          dec_min =-10., dec_max = 10.)
        
        self.assertRaises(ValueError,ObservationMetaData,box_bounds=box_bounds,circ_bounds=circ_bounds)
        self.assertRaises(ValueError,ObservationMetaData,box_bounds=box_bounds,m5=m5tuple)
        
        obsMD = ObservationMetaData(box_bounds=box_bounds,m5=m5dict)
        self.assertRaises(ValueError,obsMD.m5,'i')
        
        obsMD = ObservationMetaData(box_bounds=box_bounds)
        self.assertRaises(ValueError,obsMD.m5,'u')
        
        

def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(ObservationMetaDataTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)

    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
