#!/usr/bin/env python
from dbModel import *
from catalogDbMap import catalogDbMap
import os
from lsst.sims.measures.instance import InstanceCatalog
from lsst.sims.measures.instance import CatalogDescription
from lsst.sims.measures.instance import Metadata
from lsst.sims.measures.instance import CatalogType


class queryDB(object):
  def __init__(self, objtype = 'star', filetypes=CatalogType.TRIM, chunksize=100000):
    setup_all()
    self._start=0
    self.filetypes = filetypes
    self.objtype = objtype
    self.chunksize=chunksize
    self.cdm = catalogDbMap()

  def getNextChunk(self):
    try:
      result = self.query.slice(self._start, self._start+self.chunksize).all()
      self._start += self.chunksize
      if len(result) == 0:
        return None
      else:
        return self.makeCatalogFromQuery(result)
    except Exception as e:
      print "Exception of type: %s"%(type(e))
      raise Exception(e)


  def getInstanceCatalogById(self, id,  opsim="3_61", add_columns=()):
    os = OpSim3_61.query.filter("obshistid=%s"%(id)).first()
    objtype = self.objtype
    if objtype == 'star':
      fscale = schema.Column('flux_scale')
      lcid = schema.Column('isvar')
      t0 = schema.Column('t0')
      obsDate = os.expmjd
      duration = schema.Column('timescale')
      fpeak = schema.Column('varfluxpeak')
      bandpass = os.filter
      mags = func.toMag(fscale*func.flux_ratio_from_lc(lcid,t0,obsDate,duration,fpeak,bandpass)).label('magNorm')
      """The following was for testing.  In the case where all stars are variable,
      this is very slow (1 hour for 300K points), but when the mag calculation
      is not done it takes ~1min.
      """
      #mags = fscale.label('magNorm')
      self.query = Star.query.add_column(mags).filter("point @ scircle \'<(%f,%f),%fd>\'"%(os.fieldra, os.fielddec, 2.1))
    elif objtype == 'wd':
      fscale = schema.Column('flux_scale')
      lcid = schema.Column('isvar')
      t0 = schema.Column('t0')
      obsDate = os.expmjd
      duration = schema.Column('timescale')
      fpeak = schema.Column('varfluxpeak')
      bandpass = os.filter
      mags = func.toMag(fscale*func.flux_ratio_from_lc(lcid,t0,obsDate,duration,fpeak,bandpass)).label('magNorm')
      """The following was for testing.  In the case where all stars are variable,
      this is very slow (1 hour for 300K points), but when the mag calculation
      is not done it takes ~1min.
      """
      #mags = fscale.label('magNorm')
      self.query = WD.query.add_column(mags).filter("point @ scircle \'<(%f,%f),%fd>\'"%(os.fieldra, os.fielddec, 2.1))
    elif objtype == 'ssm':
      pass
    elif objtype == 'galaxy':
      pass
    else:
      raise Exception('getInstanceCatalogById', 'Did not give valid object type')
    self.metadata = Metadata()
    for k in self.cdm.metadataMap.keys():
      self.metadata.addMetadata(k,os.__dict__[self.cdm.metadataMap[k]['opsim3_61']],"")
    result = self.query.slice(self._start, self._start+self.chunksize).all()
    self._start += self.chunksize
    if len(result) == 0:
      return None
    else:
      return self.makeCatalogFromQuery(result)

  def makeCatalogFromQuery(self, result):
    if os.environ.has_key("CATALOG_DESCRIPTION_PATH"):
      catalogDescriptionPath = os.environ["CATALOG_DESCRIPTION_PATH"]
    else:
      raise Exception("Environment variable CATALOG_DESCRIPTION_PATH not set to location of the catalog description files")
    nic = InstanceCatalog.InstanceCatalog()
    nic.catalogDescription = CatalogDescription.CatalogDescription(
                   catalogDescriptionPath+"requiredMetadata.dat",
                   catalogDescriptionPath+"requiredSchemaFields.dat",
                   catalogDescriptionPath+"requiredDerivedFields.dat",
                   catalogDescriptionPath+"outputFormat.dat")
    nic.metadata.catalogDescription =  nic.catalogDescription
    nic.catalogType = self.filetypes
    data = {}
    for k in self.cdm.objectTypes['POINT'].keys():
      data[k] = []
    for s in result:
      for k in self.cdm.objectTypes['POINT'].keys():
	if k == 'magNorm':
          data[k].append(s.magNorm)
        elif k == 'shearXX':
          data[k].append(self.cdm.objectTypes['POINT'][k]['star'])
        elif k == 'shearYY':
          data[k].append(self.cdm.objectTypes['POINT'][k]['star'])
        elif k == 'magnification':
          data[k].append(self.cdm.objectTypes['POINT'][k]['star'])
        elif k == 'spatialmodel':
          data[k].append(self.cdm.objectTypes['POINT'][k]['star'])
        elif k == 'galacticExtinctionModel':
          data[k].append(self.cdm.objectTypes['POINT'][k]['star'])
        elif k == 'galacticRv':
          data[k].append(self.cdm.objectTypes['POINT'][k]['star'])
        elif k == 'internalExtinctionModel':
          data[k].append(self.cdm.objectTypes['POINT'][k]['star'])
        elif k == 'galacticAv':
          data[k].append(s.Star.ebv*3.1)
	else:
          data[k].append(s.Star.__dict__[self.cdm.objectTypes['POINT'][k]['star']])
    for k in self.cdm.objectTypes['POINT'].keys():
      nic.addColumn(data[k], k)
    nic.metadata = self.metadata
    return nic
