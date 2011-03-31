#!/usr/bin/env python
import pyoorb,math
import exceptions,warnings
import lsst.sims.catalogs.measures.utils as mUtils
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.generation.db import jobDB

if __name__ == "__main__":
  csize = 10000
  cattype = "TEST"
  objtypes = ['ALLSTARS']
  varobj = ['ALLSTARS', 'AGN', 'IMAGE']
  warnings.simplefilter('ignore', category=exceptions.UserWarning)
  for objtype in objtypes:
      outfile = "test_%s.dat"%(objtype)
      print "doing %s"%(objtype)
      myqdb = queryDB.queryDB(chunksize=csize,objtype=objtype,filetypes=[cattype])
      ic = myqdb.getInstanceCatalogById(85520357, radiusdeg=0.5)
      cnum = 0
      while ic is not None:
          ic.validateData('TEST')
          ic.writeCatalogData(outfile, "TEST", newfile = False)
          ic = myqdb.getNextChunk()
          cnum += 1
      myqdb.closeSession()
