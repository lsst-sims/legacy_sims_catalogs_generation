#!/usr/bin/env python
import pyoorb,math
import time
import lsst.sims.catalogs.measures.utils as mUtils
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.generation.db import jobDB

if __name__ == "__main__":
  csize = 10
  cattype = "TRIM"
  myqdb = queryDB.queryDB(chunksize=csize,objtype="AGN")
  ic = myqdb.getInstanceCatalogById(85748128, radiusdeg=.1)
  ic.makeTrimCoords()
  mUtils.trimGeneration.derivedTrimMetadata(ic)
  ic.metadata.validateMetadata(cattype, myqdb.opsim) 
  ic.metadata.writeMetadata("test.dat", cattype, myqdb.opsim,\
         newfile=True) 
  ic.validateData('TRIM')
  keys = ic.dataArray.keys()
  for row in xrange(len(ic.dataArray['raJ2000'])):
    for k in keys:
       print ic.dataArray[k][row],
    print 
  ic.writeCatalogData("test.dat", "TRIM", newfile = False)
  ic = myqdb.getNextChunk()
  cnum = 0
  while ic is not None:
    ic.makeTrimCoords()
    ic.writeCatalogData("test.dat", "TRIM", newfile = False)
    ic = myqdb.getNextChunk()
    cnum += 1

