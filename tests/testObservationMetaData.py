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
    def testInit(self):
        m5tuple = (0,1,2,3)
        m5float = 25.
        m5dict = dict(u=25., g=23., r=22.)
        circ_bounds = dict(ra = 25., dec= 50., radius = 5.)
        box_bounds = dict(ra_min = 10., ra_max = 20., 
                          dec_min =-10., dec_max = 10.)
        
        #make sure ObservationMetaData raises an exception when you try to
        #set both box bounds and circular bounds
        self.assertRaises(ValueError,ObservationMetaData,box_bounds=box_bounds,circ_bounds=circ_bounds)
        
        #make sure that ObservationMetaData raises an exception when you
        #try to set m5 to something that is neither float nor dict
        self.assertRaises(ValueError,ObservationMetaData,box_bounds=box_bounds,m5=m5tuple)
        
        #make sure ObservationMetaData.m5() throws an error when it does
        #not have the data you want
        obsMD = ObservationMetaData(box_bounds=box_bounds)
        self.assertRaises(ValueError,obsMD.m5,'u')
        obsMD = ObservationMetaData(box_bounds=box_bounds,m5=m5dict)
        self.assertRaises(ValueError,obsMD.m5,'i')
        
        #make sure that ObservationMetaData.m5() returns the correct values
        self.assertAlmostEqual(obsMD.m5('u'),m5dict['u'],10)
        self.assertAlmostEqual(obsMD.m5('g'),m5dict['g'],10)
        self.assertAlmostEqual(obsMD.m5('r'),m5dict['r'],10)
        
        obsMD = ObservationMetaData(box_bounds=box_bounds, m5=m5float)
        self.assertAlmostEqual(obsMD.m5('u'),m5float,10)
        self.assertAlmostEqual(obsMD.m5('sally'),m5float,10)
             
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
