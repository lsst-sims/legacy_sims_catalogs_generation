#!/usr/bin/env python
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.generation.db import jobDB

if __name__ == "__main__":
  myqdb = queryDB.queryDB(chunksize=1000)
  mj = jobDB.LogEvents()
  mj.registerTaskStart()
  ic = myqdb.getInstanceCatalogById(85748128)

  while ic is not None:
      print myqdb._start
      ic = myqdb.getNextChunk()
