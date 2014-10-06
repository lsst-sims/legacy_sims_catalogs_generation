import os
import numpy
import unittest
import lsst.utils.tests as utilsTests
from lsst.sims.catalogs.generation.db.spatialBounds import SpatialBounds

class SpatialBoundsTest(unittest.TestCase):

    def testCircle(self):
        myFov = SpatialBounds.getSpatialBounds('circle',20.0,30.0,1.0)
        self.assertEqual(myFov.RA,20.0)
        self.assertEqual(myFov.DEC,30.0)
        self.assertEqual(myFov.radius,1.0)
    
    def testSquare(self):
        myFov1 = SpatialBounds.getSpatialBounds('box',20.0,30.0,2.0)
        self.assertEqual(myFov1.RA,20.0)
        self.assertEqual(myFov1.DEC,30.0)
        self.assertEqual(myFov1.RAmax,22.0)
        self.assertEqual(myFov1.RAmin,18.0)
        self.assertEqual(myFov1.DECmax,32.0)
        self.assertEqual(myFov1.DECmin,28.0)

        length = [2.0]
        myFov2 = SpatialBounds.getSpatialBounds('box',20.0,30.0,length)
        self.assertEqual(myFov2.RA,20.0)
        self.assertEqual(myFov2.DEC,30.0)
        self.assertEqual(myFov2.RAmax,22.0)
        self.assertEqual(myFov2.RAmin,18.0)
        self.assertEqual(myFov2.DECmax,32.0)
        self.assertEqual(myFov2.DECmin,28.0)
        
        length = (2.0)
        myFov3 = SpatialBounds.getSpatialBounds('box',20.0,30.0,length)
        self.assertEqual(myFov3.RA,20.0)
        self.assertEqual(myFov3.DEC,30.0)
        self.assertEqual(myFov3.RAmax,22.0)
        self.assertEqual(myFov3.RAmin,18.0)
        self.assertEqual(myFov3.DECmax,32.0)
        self.assertEqual(myFov3.DECmin,28.0)

        length = numpy.array([2.0])
        myFov4 = SpatialBounds.getSpatialBounds('box',20.0,30.0,length)
        self.assertEqual(myFov4.RA,20.0)
        self.assertEqual(myFov4.DEC,30.0)
        self.assertEqual(myFov4.RAmax,22.0)
        self.assertEqual(myFov4.RAmin,18.0)
        self.assertEqual(myFov4.DECmax,32.0)
        self.assertEqual(myFov4.DECmin,28.0)

        self.assertRaises(RuntimeError,SpatialBounds.getSpatialBounds,
                          'utterNonsense',20.0,30.0,length)

    def testRectangle(self):
    
        length = [2.0,3.0]
        myFov2 = SpatialBounds.getSpatialBounds('box',20.0,30.0,length)
        self.assertEqual(myFov2.RA,20.0)
        self.assertEqual(myFov2.DEC,30.0)
        self.assertEqual(myFov2.RAmax,22.0)
        self.assertEqual(myFov2.RAmin,18.0)
        self.assertEqual(myFov2.DECmax,33.0)
        self.assertEqual(myFov2.DECmin,27.0)
        
        length = (2.0,3.0)
        myFov3 = SpatialBounds.getSpatialBounds('box',20.0,30.0,length)
        self.assertEqual(myFov3.RA,20.0)
        self.assertEqual(myFov3.DEC,30.0)
        self.assertEqual(myFov3.RAmax,22.0)
        self.assertEqual(myFov3.RAmin,18.0)
        self.assertEqual(myFov3.DECmax,33.0)
        self.assertEqual(myFov3.DECmin,27.0)

        length = numpy.array([2.0,3.0])
        myFov4 = SpatialBounds.getSpatialBounds('box',20.0,30.0,length)
        self.assertEqual(myFov4.RA,20.0)
        self.assertEqual(myFov4.DEC,30.0)
        self.assertEqual(myFov4.RAmax,22.0)
        self.assertEqual(myFov4.RAmin,18.0)
        self.assertEqual(myFov4.DECmax,33.0)
        self.assertEqual(myFov4.DECmin,27.0)

        self.assertRaises(RuntimeError,SpatialBounds.getSpatialBounds,
                          'box',20.0,30.0,'moreUtterNonsense')
            
def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(SpatialBoundsTest)

    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
