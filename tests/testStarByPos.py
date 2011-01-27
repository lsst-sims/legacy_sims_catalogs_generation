#!/usr/bin/env python
import pyoorb
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.measures.astrometry import Bbox

if __name__ == "__main__":
  csize = 100
  myqdb = queryDB.queryDB(chunksize=csize,objtype="ALLSTARS")
  ic = myqdb.getInstanceCatalogByCirc(centradeg=210, centdecdeg=-5,
          radiusdeg=0.1)
  keys =ic.dataArray.keys()
  print ",".join(keys)
  while ic is not None:
    commdstr = "zip(%s)"%(",".join(["ic.dataArray[\'%s\']"%k for k in keys]))
    for l in eval(commdstr):
      print ",".join([str(el) for el in l])
    ic = myqdb.getNextChunk()
