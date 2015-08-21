from __future__ import with_statement
import unittest
import numpy
import os
import lsst.utils.tests as utilsTests
from lsst.utils import getPackageDir

from lsst.sims.catalogs.generation.db import fileDBObject, \
                                      CompoundCatalogDBObject, \
                                      CatalogDBObject

class dbClass1(CatalogDBObject):
    objid = 1
    idColKey = 'id'
    tableid = 'test'
    columns = [('aa', 'a'),
               ('bb', 'd', str, 20)]

    dbDefaultValues = {'ee': -1}


class dbClass2(CatalogDBObject):
    objid = 2
    idColKey = 'id'
    tableid = 'test'
    columns = [('aa', '2.0*b'),
               ('bb', 'a')]

    dbDefaultValues = {'ee': -2}


class dbClass3(CatalogDBObject):
    objid = 3
    idColKey = 'id'
    tableid = 'test'
    columns = [('aa', 'c-3.0'),
               ('bb', 'a'),
               ('cc', '3.0*b')]

    dbDefaultValues = {'ee': -3}


class dbClass4(CatalogDBObject):
    objid = 4
    idColKey = 'id'
    tableid = 'otherTest'
    columns = [('aa', 'c-3.0'),
               ('bb', 'a'),
               ('cc', '3.0*b')]

    dbDefaultValues = {'ee': -3}



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

        colNames = ['db_0_aa', 'db_0_bb',
                    'db_1_aa', 'db_1_bb',
                    'db_2_aa', 'db_2_bb', 'db_2_cc']

        results = compoundDb.query_columns(colnames=colNames)

        for chunk in results:
            numpy.testing.assert_array_almost_equal(chunk['db_0_aa'],
                                                    self.controlArray['a'],
                                                    decimal=6)

            numpy.testing.assert_array_equal(chunk['db_0_bb'],
                                             self.controlArray['d'])

            numpy.testing.assert_array_almost_equal(chunk['db_1_aa'],
                                                    2.0*self.controlArray['b'],
                                                    decimal=6)

            numpy.testing.assert_array_almost_equal(chunk['db_1_bb'],
                                                    self.controlArray['a'],
                                                    decimal=6)


            numpy.testing.assert_array_almost_equal(chunk['db_2_aa'],
                                                    self.controlArray['c']-3.0,
                                                    decimal=6)


            numpy.testing.assert_array_almost_equal(chunk['db_2_bb'],
                                                    self.controlArray['a'],
                                                    decimal=6)

            numpy.testing.assert_array_almost_equal(chunk['db_2_cc'],
                                                    3.0*self.controlArray['b'],
                                                    decimal=6)

def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(CompoundCatalogDBObjectTestCase)


    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
