import sqlite3
from numpy.random import random, seed
from sqlite3 import dbapi2 as sqlite
import numpy

from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData

def writeResult(result, fname):
    fh = open(fname, 'w')
    first = True
    for chunk in result:
        if first:
            fh.write(",".join([str(el) for el in chunk.dtype.names])+"\n")
            first = False
        for i in xrange(len(chunk)):
            fh.write(",".join([str(chunk[name][i]) for name in chunk.dtype.names])+"\n")
    fh.close()

class myTestStars(DBObject):
    objid = 'teststars'
    tableid = 'stars'
    idColKey = 'id'
    #Make this implausibly large?  
    appendint = 1023
    dbAddress = 'sqlite:///testDatabase.db'
    raColName = 'ra'
    decColName = 'decl'
    spatialModel = 'POINT'
    columns = [('id', None, int),
               ('raJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('decJ2000', 'decl*%f'%(numpy.pi/180.)),
               ('umag', None),
               ('gmag', None),
               ('rmag', None),
               ('imag', None),
               ('zmag', None),
               ('ymag', None),
               ('mag_norm', None)]

def sampleSphere(size):
    #From Shao 1996: "Spherical Sampling by Archimedes' Theorem"
    ra = random(size)*2.*numpy.pi
    z = random(size)*2. - 1.
    dec = numpy.arccos(z) - numpy.pi/2.
    return ra, dec

def makeTestDB(size=1000):
    conn = sqlite3.connect('testDatabase.db')
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE stars
                     (id int, ra real, decl real, umag real, gmag real, rmag real, 
                     imag real, zmag real, ymag real, mag_norm real)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")
    seed(1)
    ra, dec = sampleSphere(size)
    #Typical colors
    umg = 1.5
    gmr = 0.65
    rmi = 1.0
    imz = 0.45
    zmy = 0.3
    mag_norm = random(size)*6. + 18.
    #assume mag norm is g-band (which is close to true)
    umag = mag_norm + umg
    gmag = mag_norm
    rmag = gmag - gmr
    imag = rmag - rmi
    zmag = imag - imz
    ymag = zmag -zmy
    for i in xrange(size):
        c.execute('''INSERT INTO stars VALUES (%i, %f, %f, %f, %f, %f, %f, %f, %f, %f)'''%\
                  (i, numpy.degrees(ra[i]), numpy.degrees(dec[i]), umag[i], gmag[i], rmag[i], imag[i], zmag[i], ymag[i], mag_norm[i]))
    c.execute('''CREATE INDEX ra_idx ON stars (ra)''')
    c.execute('''CREATE INDEX dec_idx ON stars (decl)''')
    conn.commit()
    conn.close()
