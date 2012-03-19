#!/usr/bin/env python
import pyoorb, copy, cPickle
from lsst.sims.catalogs.generation.db import queryDB
import lsst.sims.catalogs.measures.utils as mUtils

tNum = 0
curMD = None
cSize = 50
obsId = 85679372
radius = 0.1
types = ['ALLSTARS']
varobj = ['ALLSTARS', 'AGN', 'IMAGE']

def doIC(ic, myQDB, curMD, tNum, isVar):
    print 'HANDLING NEW IC'
    mUtils.trimGeneration.derivedTrimMetadata(ic)
    if curMD == None: curMD = copy.deepcopy(ic.metadata)
    else: curMD.mergeMetadata(ic.metadata)
    tBase = 'aT6IC%i' % tNum
    print '   WRITING TO PICKLE'
    cPickle.dump(ic, open(tBase + '.p', 'w'))
    print '   READING FROM PICKLE'
    icNew = cPickle.load(open(tBase + '.p'))
    if isVar:
        print '   DOING VARIABILITY'  
        ic.applyVariability()
    icNew.makeTrimCoords()
    icNew.validateData('TRIM')
    icNew.writeCatalogData(tBase + '.txt', 'TRIM')
    return curMD

def doQueryType(t, curMD, tNum, cSize=cSize, obsId=obsId):
    print 'NOW QUERYING:', t
    myQDB = queryDB.queryDB(chunksize=cSize, objtype=t)
    ic = myQDB.getInstanceCatalogById(obsId, radiusdeg=radius)
    if t in varobj:
        isVar = True
    else:
	isVar = False
    while ic != None:
        curMD = doIC(ic, myQDB, curMD, tNum, isVar)
        tNum += 1
        ic = myQDB.getNextChunk()
    return curMD, tNum, myQDB

for t in types:
        curMD, tNum, myQDB = doQueryType(t, curMD, tNum)

curMD.writeMetadata('aT6.meta','TRIM', myQDB.opsim, newfile = True)


