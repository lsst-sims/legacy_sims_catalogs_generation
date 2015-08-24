from __future__ import with_statement
import unittest
import numpy
import os
import lsst.utils.tests as utilsTests
from lsst.utils import getPackageDir

from lsst.sims.utils import ObservationMetaData
from lsst.sims.catalogs.generation.db import fileDBObject, \
                                      CompoundCatalogDBObject, \
                                      CatalogDBObject

class dbClass1(CatalogDBObject):
    objid = 'class1'
    idColKey = 'id'
    tableid = 'test'
    columns = [('aa', 'a'),
               ('bb', 'd', str, 20)]

    dbDefaultValues = {'ee': -1}


class dbClass2(CatalogDBObject):
    objid = 'class2'
    idColKey = 'id'
    tableid = 'test'
    columns = [('aa', '2.0*b'),
               ('bb', 'a')]

    dbDefaultValues = {'ee': -2}


class dbClass3(CatalogDBObject):
    objid = 'class3'
    idColKey = 'id'
    tableid = 'test'
    columns = [('aa', 'c-3.0'),
               ('bb', 'a'),
               ('cc', '3.0*b')]

    dbDefaultValues = {'ee': -3}


class dbClass4(CatalogDBObject):
    objid = 'class4'
    idColKey = 'id'
    tableid = 'otherTest'
    columns = [('aa', 'c-3.0'),
               ('bb', 'a'),
               ('cc', '3.0*b')]

    dbDefaultValues = {'ee': -3}


class dbClass5(CatalogDBObject):
    objid = 'class4'
    idColKey = 'id'
    tableid = 'otherTest'
    columns = [('aa', 'c-3.0'),
               ('bb', 'a'),
               ('cc', '3.0*b')]

    dbDefaultValues = {'ee': -3}


class dbClass6(CatalogDBObject):
    objid = 'class6'
    idColKey = 'id'
    tableid = 'test'
    columns = [('a', None),
               ('b',None)]



class CompoundCatalogDBObjectTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        numpy.random.seed(42)
        dtype = numpy.dtype([
                            ('a', numpy.float),
                            ('b', numpy.float),
                            ('c', numpy.float),
                            ('d', str, 20)
                            ])

        nSamples=5
        aList = numpy.random.random_sample(nSamples)*10.0
        bList = numpy.random.random_sample(nSamples)*(-1.0)
        cList = numpy.random.random_sample(nSamples)*10.0-5.0
        ww = 'a'
        dList = []
        for ix in range(nSamples):
            ww += 'b'
            dList.append(ww)

        cls.controlArray = numpy.rec.fromrecords([
                                                 (aa, bb, cc, dd) \
                                                 for aa, bb, cc ,dd in \
                                                 zip(aList, bList, cList, dList)
                                                 ], dtype=dtype)


        baseDir = os.path.join(getPackageDir('sims_catalogs_generation'),
                               'tests', 'scratchSpace')

        cls.textFileName = os.path.join(baseDir,'compound_test_data.txt')
        if os.path.exists(cls.textFileName):
            os.unlink(cls.textFileName)

        with open(cls.textFileName, 'w') as output:
            output.write('# id a b c d\n')
            for ix, (aa, bb, cc, dd) in enumerate(zip(aList, bList, cList, dList)):
                output.write('%d %e %e %e %s\n' % (ix, aa, bb, cc, dd))



        cls.dbName =  os.path.join(baseDir, 'compoundCatalogTestDB.db')
        if os.path.exists(cls.dbName):
            os.unlink(cls.dbName)

        cls.otherDbName = os.path.join(baseDir, 'otherDb.db')
        if os.path.exists(cls.otherDbName):
            os.unlink(cls.otherDbName)

        dtype = numpy.dtype([
                            ('id', numpy.int),
                            ('a', numpy.float),
                            ('b', numpy.float),
                            ('c', numpy.float),
                            ('d', str, 20)
                            ])

        fdbo = fileDBObject(cls.textFileName, runtable='test',
                            database=cls.dbName, dtype=dtype,
                            idColKey='id')

        fdbo = fileDBObject(cls.textFileName, runtable='test',
                            database=cls.otherDbName, dtype=dtype,
                            idColKey='id')

        fdbo = fileDBObject(cls.textFileName, runtable='otherTest',
                            database=cls.dbName, dtype=dtype,
                            idColKey='id')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.textFileName):
            os.unlink(cls.textFileName)
        if os.path.exists(cls.dbName):
            os.unlink(cls.dbName)
        if os.path.exists(cls.otherDbName):
            os.unlink(cls.otherDbName)


    def testExceptions(self):
        """
        Verify that CompoundCatalogDBObject raises an exception
        when you pass it CatalogDBObjects that do not query the
        same table of the same database
        """

        #test case where they are querying the same database, but different
        #tables
        db1 = dbClass1(database=self.otherDbName, driver='sqlite')
        db2 = dbClass2(database=self.dbName, driver='sqlite')

        with self.assertRaises(RuntimeError) as context:
            compound = CompoundCatalogDBObject([db1, db2])

        self.assertTrue("['%s', '%s']" % (self.otherDbName, self.dbName) \
                        in context.exception.message)

        #test case where they are querying the same table, but different
        #databases
        db1 = dbClass4(database=self.dbName, driver='sqlite')
        db2 = dbClass2(database=self.dbName, driver='sqlite')

        with self.assertRaises(RuntimeError) as context:
            compound = CompoundCatalogDBObject([db1, db2])

        self.assertTrue("['otherTest', 'test']" in context.exception.message)

        db1 = dbClass4(database=self.dbName, driver='sqlite')
        db2 = dbClass5(database=self.dbName, driver='sqlite')
        with self.assertRaises(RuntimeError) as context:
            compound = CompoundCatalogDBObject([db1, db2])

        self.assertTrue("objid class4 is duplicated" in context.exception.message)


    def testCompoundCatalogDBObject(self):
        """
        Verify that CompoundCatalogDBObject returns the expected
        columns.
        """
        db1 = dbClass1(database=self.dbName, driver='sqlite')
        db2 = dbClass2(database=self.dbName, driver='sqlite')
        db3 = dbClass3(database=self.dbName, driver='sqlite')
        dbList = [db1, db2, db3]
        compoundDb = CompoundCatalogDBObject(dbList)

        colNames = ['class1_aa', 'class1_bb',
                    'class2_aa', 'class2_bb',
                    'class3_aa', 'class3_bb', 'class3_cc']

        results = compoundDb.query_columns(colnames=colNames)

        for chunk in results:
            numpy.testing.assert_array_almost_equal(chunk['class1_aa'],
                                                    self.controlArray['a'],
                                                    decimal=6)

            numpy.testing.assert_array_equal(chunk['class1_bb'],
                                             self.controlArray['d'])

            numpy.testing.assert_array_almost_equal(chunk['class2_aa'],
                                                    2.0*self.controlArray['b'],
                                                    decimal=6)

            numpy.testing.assert_array_almost_equal(chunk['class2_bb'],
                                                    self.controlArray['a'],
                                                    decimal=6)


            numpy.testing.assert_array_almost_equal(chunk['class3_aa'],
                                                    self.controlArray['c']-3.0,
                                                    decimal=6)


            numpy.testing.assert_array_almost_equal(chunk['class3_bb'],
                                                    self.controlArray['a'],
                                                    decimal=6)

            numpy.testing.assert_array_almost_equal(chunk['class3_cc'],
                                                    3.0*self.controlArray['b'],
                                                    decimal=6)


    def testNoneMapping(self):
        """
        Test that Nones are handled correctly in the CatalogDBObject
        column mappings
        """
        db1 = dbClass1(database=self.dbName, driver='sqlite')
        db2 = dbClass6(database=self.dbName, driver='sqlite')
        colNames = ['class1_aa', 'class1_bb', 'class6_a', 'class6_b']
        compoundDb = CompoundCatalogDBObject([db1, db2])
        results = compoundDb.query_columns(colnames=colNames)
        for chunk in results:
            numpy.testing.assert_array_almost_equal(chunk['class1_aa'],
                                                    self.controlArray['a'],
                                                    decimal=6)

            numpy.testing.assert_array_equal(chunk['class1_bb'],
                                             self.controlArray['d'])

            numpy.testing.assert_array_almost_equal(chunk['class6_a'],
                                                    self.controlArray['a'],
                                                    decimal=6)

            numpy.testing.assert_array_almost_equal(chunk['class6_b'],
                                                    self.controlArray['b'],
                                                    decimal=6)


class testStarDB1(CatalogDBObject):
    tableid = 'test'
    raColName = 'ra'
    decColName = 'dec'
    idColKey = 'id'
    objid = 'testStar1'
    columns = [('id', None),
               ('raJ2000', 'ra'),
               ('decJ2000', 'dec'),
               ('magMod', 'mag')]


class testStarDB2(CatalogDBObject):
    tableid = 'test'
    raColName = 'ra'
    decColName = 'dec'
    idColKey = 'id'
    objid = 'testStar2'
    columns = [('id', None),
               ('raJ2000', '2.0*ra'),
               ('decJ2000', '2.0*dec'),
               ('magMod', '2.0*mag')]


class CompoundWithObsMetaData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.baseDir = os.path.join(getPackageDir('sims_catalogs_generation'),
                                   'tests', 'scratchSpace')


        cls.textFileName = os.path.join(cls.baseDir, 'compound_obs_metadata_text_data.txt')

        numpy.random.seed(42)
        nSamples = 100
        raList = numpy.random.random_sample(nSamples)*360.0
        decList = numpy.random.random_sample(nSamples)*180.0 - 90.0
        magList = numpy.random.random_sample(nSamples)*15.0 + 7.0

        dtype = numpy.dtype([
                            ('ra', numpy.float),
                            ('dec', numpy.float),
                            ('mag', numpy.float)
                            ])

        cls.controlArray = numpy.rec.fromrecords([
                                                  (r, d, m) \
                                                  for r, d, m in \
                                                  zip(raList, decList, magList)
                                                  ], dtype=dtype)

        dbDtype = numpy.dtype([
                              ('id', numpy.int),
                              ('ra', numpy.float),
                              ('dec', numpy.float),
                              ('mag', numpy.float)
                              ])

        if os.path.exists(cls.textFileName):
            os.unlink(cls.textFileName)

        with open(cls.textFileName,'w') as output:
            output.write('# id ra dec mag\n')
            for ix, (r, d, m) in enumerate(zip(raList, decList, magList)):
                output.write('%d %.20f %.20f %.20f\n' % (ix, r, d, m))

        cls.dbName = os.path.join(cls.baseDir,'compound_obs_metadata_db.db')

        if os.path.exists(cls.dbName):
            os.unlink(cls.dbName)

        fdbo = fileDBObject(cls.textFileName, runtable='test',
                            database=cls.dbName, dtype=dbDtype,
                            idColKey='id')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.textFileName):
            os.unlink(cls.textFileName)

        if os.path.exists(cls.dbName):
            os.unlink(cls.dbName)


    def testObsMetaData(self):
        """
        Test that CompoundCatalogDBObject can handle ObservationMetaData
        properly
        """

        obs = ObservationMetaData(unrefractedRA = 180.0,
                                  unrefractedDec = 0.0,
                                  boundType = 'box',
                                  boundLength = (80.0, 25.0))

        db1 = testStarDB1(database=self.dbName, driver='sqlite')
        db2 = testStarDB2(database=self.dbName, driver='sqlite')

        compoundDb = CompoundCatalogDBObject([db1, db2])

        colnames = ['testStar1_id',
                    'testStar1_raJ2000', 'testStar1_decJ2000', 'testStar1_magMod',
                    'testStar2_raJ2000', 'testStar2_decJ2000', 'testStar2_magMod']

        results = compoundDb.query_columns(colnames=colnames,
                                           obs_metadata=obs)

        good_rows = []
        for chunk in results:
            for line in chunk:
                ix = line['id']
                good_rows.append(ix)
                self.assertAlmostEqual(line['testStar1_raJ2000'], self.controlArray['ra'][ix], 10)
                self.assertAlmostEqual(line['testStar1_decJ2000'], self.controlArray['dec'][ix], 10)
                self.assertAlmostEqual(line['testStar1_magMod'], self.controlArray['mag'][ix], 10)
                self.assertAlmostEqual(line['testStar2_raJ2000'], 2.0*self.controlArray['ra'][ix], 10)
                self.assertAlmostEqual(line['testStar2_decJ2000'], 2.0*self.controlArray['dec'][ix], 10)
                self.assertAlmostEqual(line['testStar2_magMod'], 2.0*self.controlArray['mag'][ix], 10)
                self.assertTrue(self.controlArray['ra'][ix]>100.0)
                self.assertTrue(self.controlArray['ra'][ix]<260.0)
                self.assertTrue(self.controlArray['dec'][ix]>-25.0)
                self.assertTrue(self.controlArray['dec'][ix]<25.0)

        bad_rows = [ix for ix in range(self.controlArray.shape[0]) if ix not in good_rows]

        in_bounds = [rr>100.0 and rr<260.0 and dd>-25.0 and dd<25.0 \
                      for (rr, dd) in \
                      zip(self.controlArray['ra'][bad_rows], self.controlArray['dec'][bad_rows])]

        self.assertFalse(True in in_bounds)
        self.assertTrue(len(good_rows)>0)
        self.assertTrue(len(bad_rows)>0)


    def testContraint(self):
        """
        Test that CompoundCatalogDBObject runs correctly with a constraint
        """
        db1 = testStarDB1(database=self.dbName, driver='sqlite')
        db2 = testStarDB2(database=self.dbName, driver='sqlite')

        compoundDb = CompoundCatalogDBObject([db1, db2])

        colnames = ['testStar1_id',
                    'testStar1_raJ2000', 'testStar1_decJ2000', 'testStar1_magMod',
                    'testStar2_raJ2000', 'testStar2_decJ2000', 'testStar2_magMod']

        results = compoundDb.query_columns(colnames=colnames,
                                           constraint='mag<11.0')

        good_rows = []
        for chunk in results:
            for line in chunk:
                ix = line['id']
                good_rows.append(ix)
                self.assertAlmostEqual(line['testStar1_raJ2000'], self.controlArray['ra'][ix], 10)
                self.assertAlmostEqual(line['testStar1_decJ2000'], self.controlArray['dec'][ix], 10)
                self.assertAlmostEqual(line['testStar1_magMod'], self.controlArray['mag'][ix], 10)
                self.assertAlmostEqual(line['testStar2_raJ2000'], 2.0*self.controlArray['ra'][ix], 10)
                self.assertAlmostEqual(line['testStar2_decJ2000'], 2.0*self.controlArray['dec'][ix], 10)
                self.assertAlmostEqual(line['testStar2_magMod'], 2.0*self.controlArray['mag'][ix], 10)
                self.assertTrue(self.controlArray['mag'][ix]<11.0)


        bad_rows = [ix for ix in range(self.controlArray.shape[0]) if ix not in good_rows]

        in_bounds = [mm<11.0 for mm in self.controlArray['mag'][bad_rows]]

        self.assertFalse(True in in_bounds)
        self.assertTrue(len(good_rows)>0)
        self.assertTrue(len(bad_rows)>0)
        self.assertEqual(len(good_rows)+len(bad_rows), self.controlArray.shape[0])


    def testObsMetadataAndConstraint(self):
        """
        Test that CompoundCatalogDBObject correctly handles an ObservationMetaData
        and a constraint at the same time
        """
        obs = ObservationMetaData(unrefractedRA = 180.0,
                                  unrefractedDec = 0.0,
                                  boundType = 'box',
                                  boundLength = (80.0, 25.0))

        db1 = testStarDB1(database=self.dbName, driver='sqlite')
        db2 = testStarDB2(database=self.dbName, driver='sqlite')

        compoundDb = CompoundCatalogDBObject([db1, db2])

        colnames = ['testStar1_id',
                    'testStar1_raJ2000', 'testStar1_decJ2000', 'testStar1_magMod',
                    'testStar2_raJ2000', 'testStar2_decJ2000', 'testStar2_magMod']

        results = compoundDb.query_columns(colnames=colnames,
                                           obs_metadata=obs,
                                           constraint='mag>15.0')

        good_rows = []
        for chunk in results:
            for line in chunk:
                ix = line['id']
                good_rows.append(ix)
                self.assertAlmostEqual(line['testStar1_raJ2000'], self.controlArray['ra'][ix], 10)
                self.assertAlmostEqual(line['testStar1_decJ2000'], self.controlArray['dec'][ix], 10)
                self.assertAlmostEqual(line['testStar1_magMod'], self.controlArray['mag'][ix], 10)
                self.assertAlmostEqual(line['testStar2_raJ2000'], 2.0*self.controlArray['ra'][ix], 10)
                self.assertAlmostEqual(line['testStar2_decJ2000'], 2.0*self.controlArray['dec'][ix], 10)
                self.assertAlmostEqual(line['testStar2_magMod'], 2.0*self.controlArray['mag'][ix], 10)
                self.assertTrue(self.controlArray['ra'][ix]>100.0)
                self.assertTrue(self.controlArray['ra'][ix]<260.0)
                self.assertTrue(self.controlArray['dec'][ix]>-25.0)
                self.assertTrue(self.controlArray['dec'][ix]<25.0)
                self.assertTrue(self.controlArray['mag'][ix]>15.0)

        bad_rows = [ix for ix in range(self.controlArray.shape[0]) if ix not in good_rows]

        in_bounds = [rr>100.0 and rr<260.0 and dd>-25.0 and dd<25.0 and mm>150 \
                      for (rr, dd, mm) in \
                      zip(self.controlArray['ra'][bad_rows], self.controlArray['dec'][bad_rows], \
                          self.controlArray['mag'][bad_rows])]

        self.assertFalse(True in in_bounds)
        self.assertTrue(len(good_rows)>0)
        self.assertTrue(len(bad_rows)>0)
        self.assertEqual(len(good_rows)+len(bad_rows), self.controlArray.shape[0])



def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(CompoundCatalogDBObjectTestCase)
    suites += unittest.makeSuite(CompoundWithObsMetaData)


    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
