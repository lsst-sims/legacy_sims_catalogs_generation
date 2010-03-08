#!/usr/bin/env python
from lsst.sims.generation.db import queryDB as qdb

if __name__ == "__main__":
  myqdb = qdb.queryDB(chunksize=10)
  ic = myqdb.getInstanceCatalogById(85748128)
