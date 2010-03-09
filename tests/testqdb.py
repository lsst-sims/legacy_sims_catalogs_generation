#!/usr/bin/env python
from lsst.sims.generation.db import queryDB

if __name__ == "__main__":
  myqdb = queryDB(chunksize=10)
  ic = myqdb.getInstanceCatalogById(85748128)
