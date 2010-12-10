#!/usr/bin/env python
import pyoorb, copy
from lsst.sims.catalogs.generation.db import queryDB
import lsst.sims.catalogs.measures.utils as mUtils

if __name__ == "__main__":
    csize = 10
    objects = ("GALAXY","ALLSTARS","SSM")
    cattype = 'TRIM'
    for obj in objects:
        myqdb = queryDB.queryDB(chunksize=csize, objtype=obj)
        ic = myqdb.getInstanceCatalogById(85748128)
        mUtils.trimGeneration.derivedTrimMetadata(ic)
        ic.makeHelio()
        ic.makeTrimCoords()
        #print ic.metadata.parameters
        #print ic.dataArray.keys()
        ic.validateData(cattype)
        curMD = copy.deepcopy(ic.metadata)
        curMD.validateMetadata(cattype, myqdb.opsim) 
        curMD.writeMetadata("hack_%s.dat"%(obj), cattype, myqdb.opsim,\
                newfile=True) 
        ic.writeCatalogData("hack_%s.dat"%(obj), cattype)

