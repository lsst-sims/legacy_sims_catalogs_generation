#!/usr/bin/env python
import pyoorb
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.measures.astrometry import Bbox

if __name__ == "__main__":
  csize = 1000
  myqdb = queryDB.queryDB(chunksize=csize,objtype="BHBSTARS")
  ic = myqdb.getInstanceCatalogById(85748128, radiusdeg=2.1)
  ic.makeTrimCoords()
  ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  ic = myqdb.getNextChunk()
  cnum = 0
  while ic is not None:
    print "done with chunk %i"%cnum
    ic.makeTrimCoords()
    ic.writeCatalogData("test.dat", "TRIM", newfile = False)
    ic = myqdb.getNextChunk()
    cnum += 1

