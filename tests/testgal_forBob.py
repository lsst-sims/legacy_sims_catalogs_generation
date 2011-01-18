#!/usr/bin/env python
import pyoorb
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.measures.astrometry import Bbox

if __name__ == "__main__":
  csize = 10000
  racent = 210.
  deccent = -5.
  radius = 0.01
  expmjd = 0.
  obj = "NEWASSEMBLEDGALAXY"
  print "Doing object type: %s"%obj
  myqdb = queryDB.queryDB(chunksize=csize,objtype=obj,filetypes=('TEST',))
  ic = myqdb.getInstanceCatalogByCirc(210.,-5.,radius,expmjd=expmjd)
  keys = ic.dataArray.keys()
  print ",".join([str(k) for k in keys])
  while ic is not None:
    for i in range(len(ic.dataArray[keys[0]])):
      line = []
      for k in keys:
        line.append(ic.dataArray[k][i])
      print ",".join([str(el) for el in line])
    ic = myqdb.getNextChunk()

