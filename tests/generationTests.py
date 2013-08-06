import os
from lsst.sims.catalogs.generation.db import DBObject, ObservationMetaData
import lsst.sims.catalogs.generation.utils.testUtils as tu

if __name__=="__main__":
    if not os.path.exists('testDatabase.db'):
        tu.makeTestDB(size=100000)

    obsMD = DBObject.from_objid('opsim3_61')
    #Observation metadata from OpSim
    obs_metadata = obsMD.getObservationMetaData(88544919, 1.75, makeCircBounds=True)
    #Observation metadata from pointing
    obs_metadata_pointed = ObservationMetaData(circ_bounds=dict(ra=210., dec=-60, radius=1.75))
    
    mystars = tu.myTestStars()
    result = mystars.query_columns(obs_metadata=obs_metadata)
    tu.writeResult(result, "test_opsim.out")
    result = mystars.query_columns(obs_metadata=obs_metadata_pointed)
    tu.writeResult(result, "test_pointed.out")
