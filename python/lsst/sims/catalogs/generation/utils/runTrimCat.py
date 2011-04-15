#!/usr/bin/env python
import pyoorb,math,sys,tarfile,os
from copy import deepcopy
import exceptions,warnings
import lsst.sims.catalogs.measures.utils as mUtils
from lsst.sims.catalogs.generation.db import queryDB

def writeJobEvent(je, event, description=''):
    if je is not None:
        if event == 'start':
            je.registerTaskStart()
        elif event == 'stop':
            je.registerTastStop()
        else:
            je.registerEvent(event, eventdescription=description)

def mvFiles(repodir, obsid, files, je = None):
    if not os.path.exists(repodir):
        os.makedirs(repodir)
    writeJobEvent(je, "MoveFiles", "Moving files for obsid %i"%(obsid))
    tar = tarfile.open(os.path.join(repodir,"obsid%i.tar.gz"%(obsid)), "w:gz")
    for file in files:
        tar.add(file)
        writeJobEvent(je, "MoveFiles", "Added file %s"%(file))
    tar.close()
       
def runTrim(csize, obsid, radius=2.1, outdir='.', repodir=None, je=None):
    if repodir is None:
        repodir = outdir
    meta = None
    opsimid = None
    files = []
    writeJobEvent(je, 'start')
    cattype = "TRIM"
    objtypes = ['GALAXY_BULGE', 'GALAXY_DISK', 'AGN', 'ALLSTARS', 'SSM',\
            'GLENS', 'IMAGE', 'EASTEREGGS']
    varobj = ['ALLSTARS', 'AGN', 'IMAGE']
    warnings.simplefilter('ignore', category=exceptions.UserWarning)
    metaOutfile = os.path.join(outdir,"obsid%i"%(obsid),"metadata_%i.dat"%(obsid))
    outPath = os.path.join(outdir,"obsid%i"%(obsid),"pops")
    if not os.path.exists(outPath):
        os.makedirs(outPath)
    writeJobEvent(je, 'MakeDirs', 'Made output directories %s'%(outPath))

    for objtype in objtypes:
        writeJobEvent(je, 'Object:%s'%(objtype), 'Doing %s out of: %s'%(objtype, ",".join(objtypes)))

        outfile = os.path.join(outPath,"trim_%i_%s.dat"%(obsid,objtype))
        myqdb = queryDB.queryDB(chunksize=csize,objtype=objtype)
        ic = myqdb.getInstanceCatalogById(obsid, radiusdeg=radius)        
        if opsimid is None:
            opsimid = myqdb.opsim
        cnum = 0
        while ic is not None:
            writeJobEvent(je, 'GetChunk', 'Got chunk #%i of length %i'%(cnum, len(ic.dataArray[ic.dataArray.keys()[0]])))
            ic.makeTrimCoords()
            writeJobEvent(je, 'MakeTrim', 'Made trim coords for chunk #%i'%(cnum))
            if cnum == 0:
                files.append(outfile)
                mUtils.trimGeneration.derivedTrimMetadata(ic)
                if meta is None:
                    meta = deepcopy(ic.metadata)
                else:
                    meta.mergeMetadata(ic.metadata)
            if objtype in varobj:
                writeJobEvent(je, 'DoVar', 'Applying variability to chunk #%i of type %s'%(cnum, objtype))
                ic.applyVariability()
            ic.validateData('TRIM')
            numRec = len(ic.dataArray[ic.dataArray.keys()[0]])
            if cnum == 0:
                ic.writeCatalogData(outfile, "TRIM", newfile = True)
                writeJobEvent(je, 'WriteChunk', 'Wrote first chunk of length %i'%(numRec))
            else:
                ic.writeCatalogData(outfile, "TRIM", newfile = False)
                writeJobEvent(je, 'WriteChunk', 'Wrote chunk #%i of length %i'%(cnum,numRec))
            ic = myqdb.getNextChunk()
            cnum += 1
        myqdb.closeSession()
    meta.validateMetadata(cattype, opsimid)
    meta.writeMetadata(metaOutfile, cattype, opsimid, newfile=True)
    files.append(metaOutfile)
    writeJobEvent(je, 'WriteMetadata', 'Wrote metadata to %s'%(outfile))
    mvFiles(repodir, obsid, files, je)
