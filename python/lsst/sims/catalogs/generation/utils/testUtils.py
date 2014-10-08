import sqlite3
from numpy.random import random, seed
from sqlite3 import dbapi2 as sqlite
import numpy, json

from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData

def getOneChunk(results):
    try:
        chunk = results.next()
    except StopIteration:
        raise RuntimeError("No results were returned.  Cannot run tests.  Try increasing the size of the"+
                           " test database")
    return chunk

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

def sampleSphere(size, ramin = 0., dra = 2.*numpy.pi):
    #From Shao 1996: "Spherical Sampling by Archimedes' Theorem"
    ra = random(size)*dra
    ra += ramin
    ra %= 2*numpy.pi
    z = random(size)*2. - 1.
    dec = numpy.arccos(z) - numpy.pi/2.
    return ra, dec


class myTestGals(DBObject):
    objid = 'testgals'
    tableid = 'galaxies'
    idColKey = 'id'
    #Make this implausibly large?  
    appendint = 1022
    dbAddress = 'sqlite:///testDatabase.db'
    raColName = 'ra'
    decColName = 'decl'
    spatialModel = 'SERSIC2D'
    columns = [('id', None, int),
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

def makeGalTestDB(filename='testDatabase.db', size=1000, seedVal=None, **kwargs):
    """
    Make a test database to serve information to the myTestGals object
    @param size: Number of rows in the database
    @param seedVal: Random seed to use
    """
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE galaxies
                     (id int, ra real, decl real, umag real, gmag real, rmag real, 
                     imag real, zmag real, ymag real, 
                     mag_norm_agn real, mag_norm_bulge real, mag_norm_disk real,
                     redshift real, a_disk real, b_disk real, a_bulge real, b_bulge real, varParamStr text)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")
    if seedVal:
        seed(seedVal)
    ra, dec = sampleSphere(size, **kwargs)
    #Typical colors for main sequece stars
    umg = 1.5
    gmr = 0.65
    rmi = 1.0
    imz = 0.45
    zmy = 0.3
    mag_norm_disk = random(size)*6. + 18.
    mag_norm_bulge = random(size)*6. + 18.
    mag_norm_agn = random(size)*6. + 19.
    redshift = random(size)*2.5

    a_disk = random(size)*2.
    flatness = random(size)*0.8 # To prevent linear galaxies
    b_disk = a_disk*(1 - flatness)

    a_bulge = random(size)*1.5
    flatness = random(size)*0.5
    b_bulge = a_bulge*(1 - flatness)

    #assume mag norm is g-band (which is close to true)
    mag_norm = -2.5*numpy.log10(numpy.power(10, mag_norm_disk/-2.5) + numpy.power(10, mag_norm_bulge/-2.5) +
                                numpy.power(10, mag_norm_agn/-2.5))
    umag = mag_norm + umg
    gmag = mag_norm
    rmag = gmag - gmr
    imag = rmag - rmi
    zmag = imag - imz
    ymag = zmag - zmy
    for i in xrange(size):
        period = random()*490. + 10.
        amp = random()*5. + 0.2
        varParam = {'varMethodName':'testVar', 'pars':{'period':period, 'amplitude':amp}}
        paramStr = json.dumps(varParam)
        qstr = '''INSERT INTO galaxies VALUES (%i, %f, %f, %f, 
                     %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
                     %f, %f, '%s')'''%\
                   (i, numpy.degrees(ra[i]), numpy.degrees(dec[i]), umag[i], gmag[i], rmag[i], imag[i],
                   zmag[i], ymag[i], mag_norm_agn[i], mag_norm_bulge[i], mag_norm_disk[i], redshift[i], 
                   a_disk[i], b_disk[i], a_bulge[i], b_bulge[i], paramStr)
        c.execute(qstr)
    c.execute('''CREATE INDEX gal_ra_idx ON galaxies (ra)''')
    c.execute('''CREATE INDEX gal_dec_idx ON galaxies (decl)''')
    conn.commit()
    conn.close()

class myTestStars(DBObject):
    objid = 'teststars'
    tableid = 'stars'
    idColKey = 'id'
    #Make this implausibly large?  
    appendint = 1023
    dbAddress = 'sqlite:///testDatabase.db'
    raColName = 'ra'
    decColName = 'decl'
    columns = [('id', None, int),
               ('raJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('decJ2000', 'decl*%f'%(numpy.pi/180.)),
               ('umag', None),
               ('gmag', None),
               ('rmag', None),
               ('imag', None),
               ('zmag', None),
               ('ymag', None),
               ('magNorm', 'mag_norm', float)]

def makeStarTestDB(filename='testDatabase.db', size=1000, seedVal=None, **kwargs):
    """
    Make a test database to serve information to the myTestStars object
    @param size: Number of rows in the database
    @param seedVal: Random seed to use
    """
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE stars
                     (id int, ra real, decl real, umag real, gmag real, rmag real, 
                     imag real, zmag real, ymag real, mag_norm real, 
                     radialVelocity real, properMotionDec real, properMotionRa real, varParamStr text)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")
    if seedVal:
        seed(seedVal)
    ra, dec = sampleSphere(size, **kwargs)
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
    ymag = zmag - zmy
    radVel = random(size)*50. - 25.
    pmRa = random(size)*4./(1000*3600.) # deg/yr
    pmDec = random(size)*4./(1000*3600.) # deg/yr
    for i in xrange(size):
        period = random()*490. + 10.
        amp = random()*5. + 0.2
        varParam = {'varMethodName':'testVar', 'pars':{'period':period, 'amplitude':amp}}
        paramStr = json.dumps(varParam)
        qstr = '''INSERT INTO stars VALUES (%i, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, '%s')'''%\
                  (i, numpy.degrees(ra[i]), numpy.degrees(dec[i]), umag[i], gmag[i], rmag[i], 
                   imag[i], zmag[i], ymag[i], mag_norm[i], radVel[i], pmRa[i], pmDec[i], paramStr)
        c.execute(qstr)
    c.execute('''CREATE INDEX star_ra_idx ON stars (ra)''')
    c.execute('''CREATE INDEX star_dec_idx ON stars (decl)''')
    conn.commit()
    conn.close()
