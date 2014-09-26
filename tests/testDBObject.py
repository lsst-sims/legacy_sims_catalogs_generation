import os
import sqlite3

import unittest, numpy
import lsst.utils.tests as utilsTests
from lsst.sims.catalogs.generation.db import DBObject

def createDB():
    """
    Create a database from generic data store in testData/CatalogsGenerationTestData.txt
    This will be used to make sure that circ_bounds and box_bounds yield the points
    they are supposed to.
    """
    if os.path.exists('testDBObjectDB.db'):
        os.unlink('testDBObjectDB.db')

    conn = sqlite3.connect('testDBObjectDB.db')
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE intTable (id int, twice int, thrice int)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")

    for ii in range(100):
        ll=2*ii
        jj=2*ll
        kk=3*ll
        cmd = '''INSERT INTO intTable VALUES (%s, %s, %s)''' % (ll,jj,kk)
        c.execute(cmd)

    conn.commit()

    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE doubleTable (id int, sqrt float, log float)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database (double).")
    for ii in range(200):
        ll=ii+1
        nn = numpy.sqrt(float(ll))
        mm = numpy.log(float(ll))

        cmd = '''INSERT INTO doubleTable VALUES (%s, %s, %s)''' % (ll,nn,mm)
        c.execute(cmd)

    conn.commit()
    conn.close()



class DBObjectTestCase(unittest.TestCase):
    createDB()
    dbAddress = 'sqlite:///testDBObjectDB.db'

    def testTableNames(self):
        """
        Test the method that returns the names of tables in a database
        """
        dbobj = DBObject(self.dbAddress)
        names = dbobj.get_table_names()
        self.assertEqual(len(names),2)
        self.assertTrue('doubleTable' in names)
        self.assertTrue('intTable' in names)

    def testColumnNames(self):
        """
        Test the method that returns the names of columns in a table
        """
        dbobj = DBObject(self.dbAddress)
        names = dbobj.get_column_names('doubleTable')
        self.assertEqual(len(names),3)
        self.assertTrue('id' in names)
        self.assertTrue('sqrt' in names)
        self.assertTrue('log' in names)

        names = dbobj.get_column_names('intTable')
        self.assertEqual(len(names),3)
        self.assertTrue('id' in names)
        self.assertTrue('twice' in names)
        self.assertTrue('thrice' in names)

        names = dbobj.get_column_names()
        keys = ['doubleTable','intTable']
        for kk in names:
            self.assertTrue(kk in keys)

        self.assertEqual(len(names['doubleTable']),3)
        self.assertEqual(len(names['intTable']),3)
        self.assertTrue('id' in names['doubleTable'])
        self.assertTrue('sqrt' in names['doubleTable'])
        self.assertTrue('log' in names['doubleTable'])
        self.assertTrue('id' in names['intTable'])
        self.assertTrue('twice' in names['intTable'])
        self.assertTrue('thrice' in names['intTable'])

    def testSingleTableQuery(self):
        """
        Test a query on a single table (using chunk iterator)
        """
        dbobj = DBObject(self.dbAddress)
        query = 'SELECT id, sqrt FROM doubleTable'
        results = dbobj.get_chunk_iterator(query)

        dtype = [
                ('id',int),
                ('sqrt',float)]

        i = 1
        for chunk in results:
            for row in chunk:
                self.assertEqual(row[0],i)
                self.assertAlmostEqual(row[1],numpy.sqrt(i))
                self.assertEqual(dtype,row.dtype)
                i += 1

        self.assertEqual(i,201)

    def testDtype(self):
        """
        Test that passing dtype to a query works

        (also test q query on a single table using .execute() directly
        """
        dbobj = DBObject(self.dbAddress)
        query = 'SELECT id, log FROM doubleTable'
        dtype = [('id',int),('log',float)]
        results = dbobj.execute(query, dtype = dtype)

        self.assertEqual(results.dtype,dtype)
        for xx in results:
            self.assertAlmostEqual(numpy.log(xx[0]),xx[1],6)

        self.assertEqual(len(results),200)

        results = dbobj.get_chunk_iterator(query, chunk_size=10, dtype=dtype)
        results.next()
        for chunk in results:
            self.assertEqual(chunk.dtype,dtype)

    def testJoin(self):
        """
        Test a join
        """
        dbobj = DBObject(self.dbAddress)
        query = 'SELECT doubleTable.id, intTable.id, doubleTable.log, intTable.thrice '
        query += 'FROM doubleTable, intTable WHERE doubleTable.id = intTable.id'
        results = dbobj.get_chunk_iterator(query, chunk_size=10)

        dtype = [
            ('id',int),
            ('id_1',int),
            ('log',float),
            ('thrice',int)]

        i = 0
        for chunk in results:
            if i<90:
                self.assertEqual(len(chunk),10)
            for row in chunk:
                self.assertEqual(2*(i+1),row[0])
                self.assertEqual(row[0],row[1])
                self.assertAlmostEqual(numpy.log(row[0]),row[2],6)
                self.assertEqual(3*row[0],row[3])
                self.assertEqual(dtype,row.dtype)
                i += 1
        self.assertEqual(i,99)
        #make sure that we found all the matches whe should have

        results = dbobj.execute(query)
        self.assertEqual(dtype,results.dtype)
        i = 0
        for row in results:
            self.assertEqual(2*(i+1),row[0])
            self.assertEqual(row[0],row[1])
            self.assertAlmostEqual(numpy.log(row[0]),row[2],6)
            self.assertEqual(3*row[0],row[3])
            i += 1
        self.assertEqual(i,99)
        #make sure we found all the matches we should have

    def testMinMax(self):
        """
        Test queries on SQL functions by using the MIN and MAX functions
        """
        dbobj = DBObject(self.dbAddress)
        query = 'SELECT MAX(thrice), MIN(thrice) FROM intTable'
        results = dbobj.execute(query)
        self.assertEqual(results[0][0],594)
        self.assertEqual(results[0][1],0)

        dtype = [('MAXthrice',int),('MINthrice',int)]
        self.assertEqual(results.dtype,dtype)

def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(DBObjectTestCase)
    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
