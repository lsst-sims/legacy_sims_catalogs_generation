#!/usr/bin/env python
import pyoorb
from lsst.sims.catalogs.generation.db import queryDB

if __name__ == "__main__":
  myqdb = queryDB.queryDB(chunksize=10,objtype="GALAXY")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="WDSTARS")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="SSM")
  ic = myqdb.getInstanceCatalogById(85748128)
  ic.makeTrimCoords()
  print ic.metadata.parameters
  ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  #for i in range(len(ic.dataArray['id'])):
  #ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  #while len(ic.dataArray) > 0:
  #  print ic.dataArray['id']
  #  ic = myqdb.getNextChunk()

