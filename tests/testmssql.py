#!/usr/bin/env python
import math,sys,time
import exceptions,warnings
import lsst.sims.catalogs.measures.utils as mUtils
from lsst.sims.catalogs.generation.db import queryDB
from lsst.sims.catalogs.generation.db import jobDB

if __name__ == "__main__":
  if len(sys.argv) == 2:
      obsid = int(sys.argv[1])
  else:
      obsid = 88533591
  csize = 5000

  objtypes = ['GLENS', 'IMAGE', 'EASTEREGGS', 'GALAXY_BULGE', 'GALAXY_DISK', 'AGN']
  #objtypes = ['ASSEMBLEDGALAXY', 'GLENS', 'EASTEREGGS', 'SSM', 'CEPHEIDSTARS', 'EBSTARS', 'MSSTARS', 'WDSTARS',
  #        'BHBSTARS', 'RRLYSTARS', 'EASTEREGGS', 'IMAGE', 'GLENS', 'ASSEMBLEDGALAXY']
  varobj = ['CEPHEIDSTARS','EBSTARS','MSSTARS', 'WDSTARS', 'BHBSTARS', 'RRLYSTARS', 'AGN', 'IMAGE']
  warnings.simplefilter('ignore', category=exceptions.UserWarning)
  for objtype in objtypes:
      outfile = "test_%i_%s.dat"%(obsid,objtype)
      refoutfile = "test_%i_%s_REF.dat"%(obsid,objtype)
      print "doing %s"%(objtype)
      myqdb = queryDB.queryDB(chunksize=csize,objtype=objtype,filetypes=['TRIM',], dithered=True)
      ic = myqdb.getInstanceCatalogById(obsid, radiusdeg=0.1, opsim="DITHEREDOPSIM361")
      cnum = 0
      while ic is not None:
          #ic.makeReferenceCoords()
          ic.makeTrimCoords()
          if cnum == 0:
              mUtils.trimGeneration.derivedTrimMetadata(ic)
              ic.metadata.validateMetadata("TRIM", myqdb.opsim) 
              ic.metadata.writeMetadata(outfile, "TRIM", myqdb.opsim,\
                     newfile=True) 
              #ic.metadata.validateMetadata("REFERENCECATALOG", myqdb.opsim) 
              #ic.metadata.writeMetadata(refoutfile, "REFERENCECATALOG", myqdb.opsim,\
              #       newfile=True) 
          if objtype in varobj:
              print "doing variability on %s"%(objtype)
              ic.applyVariability()
          ic.validateData('TRIM')
          #ic.validateData('REFERENCECATALOG')
          ic.writeCatalogData(outfile, "TRIM", newfile = False)
          #ic.writeCatalogData(refoutfile, "REFERENCECATALOG", newfile = False)
          ic = myqdb.getNextChunk()
          cnum += 1
          print "cnum ",cnum
      myqdb.closeSession()
