#!/usr/bin/env python
import pyoorb,math
import lsst.sims.catalogs.measures.utils as mUtils
from lsst.sims.catalogs.generation.db import queryDB

if __name__ == "__main__":
  csize = 1000
  cattype = "TRIM"
  myqdb = queryDB.queryDB(chunksize=csize,objtype="GALAXY_BULGE")
  ic = myqdb.getInstanceCatalogById(85748128, radiusdeg=2.1)
  mUtils.trimGeneration.derivedTrimMetadata(ic)
  ic.metadata.validateMetadata(cattype, myqdb.opsim) 
  ic.metadata.writeMetadata("test.dat", cattype, myqdb.opsim,\
         newfile=True) 
  ic.makeTrimCoords()
  ic.writeCatalogData("test.dat", "TRIM", newfile = False)
  ic = myqdb.getNextChunk()
  cnum = 0
  while ic is not None:
    print "done with chunk %i"%cnum
    ic.makeTrimCoords()
    ic.writeCatalogData("test.dat", "TRIM", newfile = False)
    ic = myqdb.getNextChunk()
    cnum += 1

