import os
import sqlite3

import unittest, numpy
import lsst.utils.tests as utilsTests
from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData
import lsst.sims.catalogs.generation.utils.testUtils as tu

# This test should be expanded to cover more of the framework
# I have filed CATSIM-90 for this.

def createNonsenseDB():
    if os.path.exists('NonsenseDB.db'):
        os.unlink('NonsenseDB.db')
    
    conn = sqlite3.connect('NonsenseDB.db')
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE test (id int, ra real, dec real, mag real)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")
    
    inFile = open('testData/CatalogsGenerationTestData.txt','r')
    for line in inFile:
        values = line.split()
        cmd = '''INSERT INTO test VALUES (%s, %s, %s, %s)''' % (values[0],values[1],values[2],values[3])
        c.execute(cmd)
    
    conn.commit()
    conn.close()
    inFile.close()
    
class myNonsenseDB(DBObject):
    objid = 'Nonsense'
    tableid = 'test'
    idColKey = 'NonsenseId'
    #Make this implausibly large?  
    appendint = 1023
    dbAddress = 'sqlite:///NonsenseDB.db'
    raColName = 'ra'
    decColName = 'dec'
    columns = [('NonsenseId', 'id', int),
               ('NonsenseRaJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('NonsenseDecJ2000', 'dec*%f'%(numpy.pi/180.)),
               ('NonsenseMag','mag',float)]


class DBObjectTestCase(unittest.TestCase):
  
    #Delete the test database if it exists and start fresh.
    if os.path.exists('testDatabase.db'):
        print "deleting database"
        os.unlink('testDatabase.db')
    tu.makeStarTestDB(size=100000, seedVal=1)
    tu.makeGalTestDB(size=100000, seedVal=1)
    createNonsenseDB()
    obsMd = ObservationMetaData(circ_bounds=dict(ra=210., dec=-60, radius=1.75),
                                     mjd=52000., bandpassName='r')
    
    inFile = open('testData/CatalogsGenerationTestData.txt','r')
    baselineData=None
    for line in inFile:
        values=line.split()
            
        if baselineData is None:
            baselineData = numpy.array([(int(values[0]),float(values[1]),
                                           float(values[2]),float(values[3]))], \
                                       dtype=[('id',int),('ra',float),('dec',float),('mag',float)])
        else:
            baselineData = numpy.append(baselineData,numpy.array([(int(values[0]),float(values[1]),
                                                                 float(values[2]),float(values[3]))],
                                                          dtype=baselineData.dtype))  
    inFile.close()
    
    
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

    def testRealQueryConstraints(self):
        mystars = DBObject.from_objid('teststars')
        mycolumns = ['id','raJ2000','decJ2000','umag','gmag','rmag','imag','zmag','ymag']
        
        #because ra and dec are stored in degrees in the data base
        myquery = mystars.query_columns(colnames = mycolumns, 
                                        constraint = 'ra < 90. and ra > 45.')
        
        tol=1.0e-3
        for chunk in myquery:
            for star in chunk:
                self.assertTrue(numpy.degrees(star[1])<90.0+tol)
                self.assertTrue(numpy.degrees(star[1])>45.0-tol)
    
    def testNonsenseConstraints(self):
        myNonsense = DBObject.from_objid('Nonsense')
        
        circObsMd = ObservationMetaData(circ_bounds=dict(ra=210., dec=-60, radius=20.0),
                                     mjd=52000., bandpassName='r')
        
        boxObsMd = ObservationMetaData(box_bounds=dict(ra_min=50.0, ra_max=150.0, 
                                       dec_min=-20.0, dex_max=30.0), mjd=52000.,bandpassName='r')
        
        #circQuery = myNonsense.query_columns(obs_metadata=circObsMd)
        
        
        
        
    def testChunking(self):
        mystars = DBObject.from_objid('teststars')
        mycolumns = ['id','raJ2000','decJ2000','umag','gmag']
        myquery = mystars.query_columns(colnames = mycolumns, chunk_size = 1000)
        
        for chunk in myquery:
            self.assertEqual(chunk.size,1000)
            for row in chunk:
                self.assertTrue(len(row),5)

    def testClassVariables(self):
        mystars = DBObject.from_objid('teststars')
        myNonsense = DBObject.from_objid('Nonsense')
        mygalaxies = DBObject.from_objid('testgals')
        
        self.assertEqual(mystars.raColName,'ra')
        self.assertEqual(mystars.decColName,'decl')
        self.assertEqual(mystars.idColKey,'id')
        self.assertEqual(mystars.dbAddress,'sqlite:///testDatabase.db')
        self.assertEqual(mystars.appendint, 1023)
        self.assertEqual(mystars.tableid,'stars')
        self.assertFalse(hasattr(mystars,'spatialModel'))
        
        self.assertEqual(mygalaxies.raColName,'ra')
        self.assertEqual(mygalaxies.decColName,'decl')
        self.assertEqual(mygalaxies.idColKey,'id')
        self.assertEqual(mygalaxies.dbAddress,'sqlite:///testDatabase.db')
        self.assertEqual(mygalaxies.appendint, 1022)
        self.assertEqual(mygalaxies.tableid,'galaxies')
        self.assertTrue(hasattr(mygalaxies,'spatialModel'))
        self.assertEqual(mygalaxies.spatialModel,'SERSIC2D')
        
        self.assertEqual(myNonsense.raColName,'ra')
        self.assertEqual(myNonsense.decColName,'dec')
        self.assertEqual(myNonsense.idColKey,'NonsenseId')
        
        self.assertTrue('teststars' in DBObject.registry)
        self.assertTrue('testgals' in DBObject.registry)
        self.assertTrue('Nonsense' in DBObject.registry)
       
        colsShouldBe = [('id',None,int),('raJ2000','ra*%f'%(numpy.pi/180.)),
                        ('decJ2000','decl*%f'%(numpy.pi/180.)),
                        ('umag',None),('gmag',None),('rmag',None),('imag',None),
                        ('zmag',None),('ymag',None),
                        ('magNorm','mag_norm',float)]
                       
        for (col,coltest) in zip(mystars.columns,colsShouldBe):
            self.assertEqual(col,coltest)
        
        colsShouldBe = [('NonsenseId', 'id', int),
               ('NonsenseRaJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('NonsenseDecJ2000', 'dec*%f'%(numpy.pi/180.)),
               ('NonsenseMag','mag',float)]
        
        for (col,coltest) in zip(myNonsense.columns,colsShouldBe):
            self.assertEqual(col,coltest)
                
        colsShouldBe = [('id', None, int),
               ('raJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('decJ2000', 'decl*%f'%(numpy.pi/180.)),
               ('umag', None),
               ('gmag', None),
               ('rmag', None),
               ('imag', None),
               ('zmag', None),
               ('ymag', None),
               ('magNormAgn', 'mag_norm_agn', None),
               ('magNormDisk', 'mag_norm_disk', None),
               ('magNormBulge', 'mag_norm_bulge', None),
               ('redshift', None),
               ('a_disk', None),
               ('b_disk', None),
               ('a_bulge', None),
               ('b_bulge', None),]
            
        for (col,coltest) in zip(mygalaxies.columns,colsShouldBe):
            self.assertEqual(col,coltest)
            
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
