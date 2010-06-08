#!/usr/bin/env python
from lsst.sims.catalogs.generation.db import queryDB

if __name__ == "__main__":
  myqdb = queryDB.queryDB(chunksize=10,objtype="STARS")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="WDSTARS")
  #myqdb = queryDB.queryDB(chunksize=10,objtype="GALAXY")
  ic = myqdb.getInstanceCatalogById(85748128)
  print ic.metadata.parameters
  while len(ic.dataArray) > 0:
    print ic.dataArray['id']
    ic = myqdb.getNextChunk()

