#!/usr/bin/env python
import pyoorb
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.measures.astrometry import Bbox

if __name__ == "__main__":
  csize = 10
  objects = ("WDSTARS","STARS","SSM","GALAXY")
  bbox = Bbox(0.,1,-1,0)
  for obj in objects:
    if obj == "SSM":
      '''Choose an mjd for the solar system objects since it doesn't make
      sense otherwise
      '''
      expmjd = 49679.
    else:
      expmjd = 0.
      radius = 1.
    print "Doing object type: %s"%obj
    myqdb = queryDB.queryDB(chunksize=csize,objtype=obj)
    ic = myqdb.getInstanceCatalogByCirc(0.,-5.,radius,expmjd=expmjd)
    print ic.metadata.parameters
    print len(ic.dataArray['ra'])
    ic = myqdb.getInstanceCatalogByBbox(bbox,expmjd=expmjd)
    print ic.metadata.parameters
    print len(ic.dataArray['ra'])
    ic = myqdb.getInstanceCatalogById(85748128)
    print ic.metadata.parameters
    print len(ic.dataArray['ra'])
  #ic.makeTrimCoords()
  #ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  #for i in range(len(ic.dataArray['id'])):
  #ic.writeCatalogData("test.dat", "TRIM", newfile = True)
  #while ic is not None:
  #  print len(ic.dataArray['ra'])
  #  ic = myqdb.getNextChunk()

