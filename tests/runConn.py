import scipy
from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData

if __name__ == '__main__':
    obsMD = DBObject.from_objid('opsim3_61')
    obs_metadata = obsMD.getObservationMetaData(88544919, 0.1, makeCircBounds=True)
    obs_metadata_gal = ObservationMetaData(circ_bounds=dict(ra=0.0,
                                                            dec=0.0,
                                                            radius=0.01))

    galaxy = DBObject.from_objid('galaxyBase')
    galaxyTiled = DBObject.from_objid('galaxyTiled')
    galaxyBulge = DBObject.from_objid('galaxyBulge')
    galaxyDisk = DBObject.from_objid('galaxyDisk')
    galaxyAgn = DBObject.from_objid('galaxyAgn')
    star = DBObject.from_objid('msstars')

    objects = [galaxy, galaxyTiled, galaxyBulge, galaxyDisk, galaxyAgn, star]

    constraints = ["gr_total_rest < 0.3", "r_ab < 20.", "mass_bulge > 1.", 
                   "DiskLSSTg < 20.", "t0_agn > 300.", "rmag < 21."]

    metadataList = [obs_metadata_gal, obs_metadata, obs_metadata, 
                    obs_metadata, obs_metadata, obs_metadata]

    for object, constraint, md in zip(objects, constraints, metadataList):
        #Get results all at once
        result = object.query_columns(obs_metadata=md, constraint=constraint)
        #Since there is only one chunck,
        result = result.next()
        if len(result) > 0:
            print ",".join(result.dtype.names)
        print "Length of returned result set of %s is: %i"%(object.objid, len(result))
        #Or using an iterator over chunks
        ntot = 0
        result = object.query_columns(obs_metadata=md, constraint=constraint, chunk_size = 9)
        for res in result:
            if not ntot:
                print ",".join(res.dtype.names)
            ntot += len(res)
        print "Length of returned result set of %s is: %i"%(object.objid, ntot)
