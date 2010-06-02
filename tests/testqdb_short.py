#!/usr/bin/env python
from lsst.sims.catalogs.generation.db import queryDB

if __name__ == "__main__":
  myqdb = queryDB.queryDB(chunksize=10)
  ic = myqdb.getInstanceCatalogById(85748128)
  print ic.metadata.parameters
  print ic.dataArray

