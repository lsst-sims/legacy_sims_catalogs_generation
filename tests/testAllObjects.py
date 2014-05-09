from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData

if __name__ == '__main__':
    obsMD = DBObject.from_objid('opsim3_61')
    obs_metadata = obsMD.getObservationMetaData(88544919, 0.1, makeCircBounds=True)
    exclusionList = ['fileDBObject', 'exampleGalaxyBase', 'opsim3_61', 'starbase']

    for objname in DBObject.registry:
    #for objname in ['wdstars',]:
        if objname in exclusionList:
            continue
        print objname
        dbobject = DBObject.from_objid(objname)
        #Get results all at once
        result = dbobject.query_columns(obs_metadata=obs_metadata)
        #Since there is only one chunck,
        try:
            result = result.next()
        except StopIteration:
            print "No results for %s"%(objname)
            continue
        if len(result) > 0:
            print ",".join(result.dtype.names)
        print "Length of returned result set of %s is: %i"%(dbobject.objid, len(result))
