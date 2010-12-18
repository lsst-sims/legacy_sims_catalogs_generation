#!/usr/bin/env python
import pyoorb
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.measures.astrometry import Bbox

if __name__ == "__main__":
  csize = 10
  myqdb = queryDB.queryDB(chunksize=csize,objtype="ALLSTARS")
  ic = myqdb.getInstanceCatalogById(85748128)
  print ic.metadata.parameters
  print ic.dataArray.keys()
  print len(ic.dataArray['ra'])
  ic.makeTrimCoords()
  ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  #while ic is not None:
  #  print len(ic.dataArray['ra'])
  #  ic = myqdb.getNextChunk()
