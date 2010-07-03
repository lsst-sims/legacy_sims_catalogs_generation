#!/usr/bin/env python
import pyoorb
from lsst.sims.catalogs.generation.db import queryDB

if __name__ == "__main__":
  #myqdb = queryDB.queryDB(chunksize=10,objtype="GALAXY")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="WDSTARS")
  myqdb = queryDB.queryDB(chunksize=100000,objtype="STARS")
  #myqdb = queryDB.queryDB(chunksize=1000,objtype="SSM")
  ic = myqdb.getInstanceCatalogById(85748128)
  #ic.makeTrimCoords()
  print ic.metadata.parameters
  #ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  #for i in range(len(ic.dataArray['id'])):
  #ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  while ic is not None:
    print len(ic.dataArray['ra'])
    ic = myqdb.getNextChunk()

