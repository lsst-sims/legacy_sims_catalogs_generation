#!/usr/bin/env python
from lsst.sims.catalogs.generation.db import queryDB

if __name__ == "__main__":
  myqdb = queryDB.queryDB(chunksize=100000,objtype="GALRAW")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="WDSTARS")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="GALAXY")
  ic = myqdb.getInstanceCatalogById(85748128)
  ic.makeHelio()
  print ic.metadata.parameters
  ic.writeCatalogData("test.dat", "GALRAW", newfile = True)
  for i in range(len(ic.dataArray['id'])):
    print len(ic.dataArray['id'])
    ic.writeCatalogData("test.dat", "GALRAW", newfile = True)
  #while len(ic.dataArray) > 0:
  #  print ic.dataArray['id']
  #  ic = myqdb.getNextChunk()

