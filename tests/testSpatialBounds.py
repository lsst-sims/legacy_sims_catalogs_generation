import os
import numpy
import unittest
import lsst.utils.tests as utilsTests
from lsst.sims.catalogs.generation.db.spatialBounds import SpatialBounds

class SpatialBoundsTest(unittest.TestCase):

    def testCircle(self):
        myFov = SpatialBounds.getSpatialBounds('circle',1.0,2.0,1.0)
        self.assertEqual(myFov.RA,1.0)
        self.assertEqual(myFov.DEC,2.0)
        self.assertEqual(myFov.radius,1.0)

    def testSquare(self):
        myFov1 = SpatialBounds.getSpatialBounds('box',1.0,2.0,1.0)
        self.assertEqual(myFov1.RA,1.0)
        self.assertEqual(myFov1.DEC,2.0)
        self.assertEqual(myFov1.RAmaxDeg,numpy.degrees(2.0))
        self.assertEqual(myFov1.RAminDeg,numpy.degrees(0.0))
        self.assertEqual(myFov1.DECmaxDeg,numpy.degrees(3.0))
        self.assertEqual(myFov1.DECminDeg,numpy.degrees(1.0))

        length = [1.0]
        myFov2 = SpatialBounds.getSpatialBounds('box',1.0,2.0,length)
        self.assertEqual(myFov2.RA,1.0)
        self.assertEqual(myFov2.DEC,2.0)
        self.assertEqual(myFov2.RAmaxDeg,numpy.degrees(2.0))
        self.assertEqual(myFov2.RAminDeg,numpy.degrees(0.0))
        self.assertEqual(myFov2.DECmaxDeg,numpy.degrees(3.0))
        self.assertEqual(myFov2.DECminDeg,numpy.degrees(1.0))

        length = (1.0)
        myFov3 = SpatialBounds.getSpatialBounds('box',1.0,2.0,length)
        self.assertEqual(myFov3.RA,1.0)
        self.assertEqual(myFov3.DEC,2.0)
        self.assertEqual(myFov3.RAmaxDeg,numpy.degrees(2.0))
        self.assertEqual(myFov3.RAminDeg,numpy.degrees(0.0))
        self.assertEqual(myFov3.DECmaxDeg,numpy.degrees(3.0))
        self.assertEqual(myFov3.DECminDeg,numpy.degrees(1.0))

        length = numpy.array([1.0])
        myFov4 = SpatialBounds.getSpatialBounds('box',1.0,2.0,length)
        self.assertEqual(myFov4.RA,1.0)
        self.assertEqual(myFov4.DEC,2.0)
        self.assertEqual(myFov4.RAmaxDeg,numpy.degrees(2.0))
        self.assertEqual(myFov4.RAminDeg,numpy.degrees(0.0))
        self.assertEqual(myFov4.DECmaxDeg,numpy.degrees(3.0))
        self.assertEqual(myFov4.DECminDeg,numpy.degrees(1.0))

        self.assertRaises(RuntimeError,SpatialBounds.getSpatialBounds,
                          'utterNonsense',1.0,2.0,length)

    def testRectangle(self):

        length = [1.0,2.0]
        myFov2 = SpatialBounds.getSpatialBounds('box',1.0,2.0,length)
        self.assertEqual(myFov2.RA,1.0)
        self.assertEqual(myFov2.DEC,2.0)
        self.assertEqual(myFov2.RAmaxDeg,numpy.degrees(2.0))
        self.assertEqual(myFov2.RAminDeg,numpy.degrees(0.0))
        self.assertEqual(myFov2.DECmaxDeg,numpy.degrees(4.0))
        self.assertEqual(myFov2.DECminDeg,numpy.degrees(0.0))

        length = (1.0,2.0)
        myFov3 = SpatialBounds.getSpatialBounds('box',1.0,2.0,length)
        self.assertEqual(myFov3.RA,1.0)
        self.assertEqual(myFov3.DEC,2.0)
        self.assertEqual(myFov3.RAmaxDeg,numpy.degrees(2.0))
        self.assertEqual(myFov3.RAminDeg,numpy.degrees(0.0))
        self.assertEqual(myFov3.DECmaxDeg,numpy.degrees(4.0))
        self.assertEqual(myFov3.DECminDeg,numpy.degrees(0.0))

        length = numpy.array([1.0,2.0])
        myFov4 = SpatialBounds.getSpatialBounds('box',1.0,2.0,length)
        self.assertEqual(myFov4.RA,1.0)
        self.assertEqual(myFov4.DEC,2.0)
        self.assertEqual(myFov4.RAmaxDeg,numpy.degrees(2.0))
        self.assertEqual(myFov4.RAminDeg,numpy.degrees(0.0))
        self.assertEqual(myFov4.DECmaxDeg,numpy.degrees(4.0))
        self.assertEqual(myFov4.DECminDeg,numpy.degrees(0.0))

        self.assertRaises(RuntimeError,SpatialBounds.getSpatialBounds,
                          'box',1.0,2.0,'moreUtterNonsense')

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
