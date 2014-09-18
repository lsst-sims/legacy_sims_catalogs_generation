import os
import unittest
import lsst.utils.tests as utilsTests
from collections import OrderedDict
from lsst.sims.catalogs.generation.db import ObservationMetaData, Site

class ObservationMetaDataTest(unittest.TestCase):
    """
    This class will test that ObservationMetaData correctly assigns
    and returns its class variables (unrefractedRA, unrefractedDec, etc.)
    
    It will also test the behavior of the m5 member variable.
    """
    def testM5(self):
        """
        Test behavior of ObservationMetaData's m5 member variable
        """
    
        m5tuple = (0,1,2,3)
        m5float = 25.
        m5dict = dict(u=25., g=23., r=22.)
        
        #make sure ObservationMetaData.m5() throws an error when it does
        #not have the data you want
        obsMD = ObservationMetaData()
        self.assertRaises(ValueError,obsMD.m5,'u')
        obsMD = ObservationMetaData(m5=m5dict)
        self.assertRaises(ValueError,obsMD.m5,'i')
        
        #make sure that ObservationMetaData.m5() returns the correct values
        self.assertAlmostEqual(obsMD.m5('u'),m5dict['u'],10)
        self.assertAlmostEqual(obsMD.m5('g'),m5dict['g'],10)
        self.assertAlmostEqual(obsMD.m5('r'),m5dict['r'],10)
        
        obsMD = ObservationMetaData(m5=m5float)
        self.assertAlmostEqual(obsMD.m5('u'),m5float,10)
        self.assertAlmostEqual(obsMD.m5('sally'),m5float,10)
        
        #make sure that ObservationMetaData raises an exception when you
        #try to set m5 to something that is neither float nor dict
        self.assertRaises(ValueError,ObservationMetaData,m5=m5tuple)

             
    def testDefault(self):
        """
        Test that ObservationMetaData's default variables are properly set
        """
    
        testObsMD = ObservationMetaData()
        
        self.assertEqual(testObsMD.unrefractedRA,None)
        self.assertEqual(testObsMD.unrefractedDec,None)
        self.assertAlmostEqual(testObsMD.rotSkyPos,0.0,10)
        self.assertEqual(testObsMD.bandpass,'r')
        self.assertAlmostEqual(testObsMD.site.longitude,-1.2320792,10)
        self.assertAlmostEqual(testObsMD.site.latitude,-0.517781017,10)
        self.assertAlmostEqual(testObsMD.site.height,2650,10)
        self.assertAlmostEqual(testObsMD.site.xPolar,0,10)
        self.assertAlmostEqual(testObsMD.site.yPolar,0,10)
        self.assertAlmostEqual(testObsMD.site.meanTemperature,284.655,10)
        self.assertAlmostEqual(testObsMD.site.meanPressure,749.3,10)
        self.assertAlmostEqual(testObsMD.site.meanHumidity,0.4,10)
        self.assertAlmostEqual(testObsMD.site.lapseRate,0.0065,10)
    
    def testSite(self):
        """
        Test that site data gets passed correctly when it is not default
        """
        testSite = Site(longitude = 2.0, latitude = -1.0, height = 4.0,
            xPolar = 0.5, yPolar = -0.5, meanTemperature = 100.0,
            meanPressure = 500.0, meanHumidity = 0.1, lapseRate = 0.1)
        
        testObsMD = ObservationMetaData(site=testSite)
    
        self.assertAlmostEqual(testObsMD.site.longitude,2.0,10)
        self.assertAlmostEqual(testObsMD.site.latitude,-1.0,10)
        self.assertAlmostEqual(testObsMD.site.height,4.0,10)
        self.assertAlmostEqual(testObsMD.site.xPolar,0.5,10)
        self.assertAlmostEqual(testObsMD.site.yPolar,-0.5,10)
        self.assertAlmostEqual(testObsMD.site.meanTemperature,100.0,10)
        self.assertAlmostEqual(testObsMD.site.meanPressure,500.0,10)
        self.assertAlmostEqual(testObsMD.site.meanHumidity,0.1,10)
        self.assertAlmostEqual(testObsMD.site.lapseRate,0.1,10)
    
    def testAssignment(self):
        """
        Test that ObservationMetaData member variables get passed correctly
        """
        
        mjd = 5120.0
        RA = 1.5
        Dec = -1.1
        rotSkyPos = -0.2
        
        testObsMD = ObservationMetaData(mjd=mjd, unrefractedRA=RA,
            unrefractedDec=Dec, rotSkyPos=rotSkyPos, bandpassName = 'z')
        
        self.assertAlmostEqual(testObsMD.mjd,5120.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedRA,1.5,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,-1.1,10)
        self.assertAlmostEqual(testObsMD.rotSkyPos,-0.2,10)
        self.assertEqual(testObsMD.bandpass,'z')
        
        phosimMD = OrderedDict([('Unrefracted_RA', (-2.0,float)), 
                                ('Unrefracted_Dec', (0.9,float)),
                                ('Opsim_rotskypos', (1.1,float)), 
                                ('Opsim_expmjd',(4000.0,float)),
                                ('Opsim_filter',('g',str))])
        
        testObsMD.assignPhoSimMetaData(phosimMD)
        
        self.assertAlmostEqual(testObsMD.mjd,4000.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedRA,-2.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,0.9,10)
        self.assertAlmostEqual(testObsMD.rotSkyPos,1.1,10)
        self.assertEqual(testObsMD.bandpass,'g')
    
    def testBothBounds(self):
        """
        Make sure ObservationMetaData throws an error when you try to set both
        circ_bounds and box_bounds
        """
        
        circ_bounds = dict(ra = 25., dec= 50., radius = 5.)
        box_bounds = dict(ra_min = 10., ra_max = 20., 
                          dec_min =-10., dec_max = 10.)
        
        #make sure ObservationMetaData raises an exception when you try to
        #set both box bounds and circular bounds
        self.assertRaises(ValueError,ObservationMetaData,box_bounds=box_bounds,circ_bounds=circ_bounds)
       
    def testBounds(self):
        """
        Test if ObservationMetaData correctly assigns the unrefracted[RA,Dec]
        when circ_bounds or box_bounds are specified
        """
        
        circ_bounds = dict(ra = 25., dec= 50., radius = 5.)
        box_bounds = dict(ra_min = 10., ra_max = 20., 
                          dec_min =-10., dec_max = 10.)
        
        
        testObsMD = ObservationMetaData(circ_bounds=circ_bounds)
        self.assertAlmostEqual(testObsMD.unrefractedRA,25.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,50.0,10)
        
        testObsMD = ObservationMetaData(box_bounds=box_bounds)
        self.assertAlmostEqual(testObsMD.unrefractedRA,15.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,0.0,10)
        
        
        testObsMD = ObservationMetaData(circ_bounds=circ_bounds,
                    unrefractedRA=35.,unrefractedDec=50.)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,25.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,50.0,10)

        testObsMD = ObservationMetaData(circ_bounds=circ_bounds,
                    unrefractedRA=25.0,unrefractedDec=56.0)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,25.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,50.0,10)
        
        testObsMD = ObservationMetaData(circ_bounds=circ_bounds,
                    unrefractedRA=21.0,unrefractedDec=51.0)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,21.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,51.0,10)
        
        testObsMD = ObservationMetaData(box_bounds=box_bounds,
                     unrefractedRA=9.0,unrefractedDec=1.0)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,15.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,0.0,10)
        
        testObsMD = ObservationMetaData(box_bounds=box_bounds,
                     unrefractedRA=21.0,unrefractedDec=1.0)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,15.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,0.0,10)
        
        testObsMD = ObservationMetaData(box_bounds=box_bounds,
                     unrefractedRA=15.0,unrefractedDec=-11.0)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,15.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,0.0,10)
        
        testObsMD = ObservationMetaData(box_bounds=box_bounds,
                     unrefractedRA=15.0,unrefractedDec=11.0)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,15.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,0.0,10)
        
        testObsMD = ObservationMetaData(box_bounds=box_bounds,
                     unrefractedRA=12.0,unrefractedDec=-8.0)
        
        self.assertAlmostEqual(testObsMD.unrefractedRA,12.0,10)
        self.assertAlmostEqual(testObsMD.unrefractedDec,-8.0,10)
        

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
