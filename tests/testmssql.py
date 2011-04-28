#!/usr/bin/env python
import pyoorb,math,sys,time
import exceptions,warnings
import lsst.sims.catalogs.measures.utils as mUtils
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.generation.db import jobDB

if __name__ == "__main__":
  if len(sys.argv) == 2:
      obsid = int(sys.argv[1])
  else:
      obsid = 88533591
  csize = 50000
  cattype = "TRIM"
  objtypes = ['ALLSTARS', 'SSM', 'GLENS', 'IMAGE', 'EASTEREGGS',
          'GALAXY_BULGE', 'GALAXY_DISK', 'AGN']
  varobj = ['ALLSTARS', 'AGN', 'IMAGE']
  warnings.simplefilter('ignore', category=exceptions.UserWarning)
  for objtype in objtypes:
      outfile = "test_%i_%s.dat"%(obsid,objtype)
      print "doing %s"%(objtype)
      myqdb = queryDB.queryDB(chunksize=csize,objtype=objtype)
      ic = myqdb.getInstanceCatalogById(obsid, radiusdeg=.1)
      cnum = 0
      while ic is not None:
          ic.makeTrimCoords()
          if cnum == 0:
              mUtils.trimGeneration.derivedTrimMetadata(ic)
              ic.metadata.validateMetadata(cattype, myqdb.opsim) 
              ic.metadata.writeMetadata(outfile, cattype, myqdb.opsim,\
                     newfile=True) 
          if objtype in varobj:
              ic.applyVariability()
          ic.validateData('TRIM')
          ic.writeCatalogData(outfile, "TRIM", newfile = False)
          ic = myqdb.getNextChunk()
          cnum += 1
      myqdb.closeSession()
