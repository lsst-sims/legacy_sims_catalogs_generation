#!/usr/bin/env python
from dbModel import *
from lsst.sims.measures.instance import instanceCatalog as ic
from lsst.sims.measures.instance import Metadata

class queryDB(object):
  def __init__(self, objtype = 'star', filetypes=("TRIM",), chunksize=100000):
    setup_all()
    self._start=0
    self.filetypes = filetypes
    self.objtype = objtype
    self.chunksize=chunksize
    self.columns = {}
    self.columns['star'] = ('id', 'ra', 'decl')

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
    for k in (os.__dict__.keys()):
      self.metadata.addMetadata(k,os.__dict__[k],"")
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

  def makeCatalogFromQuery(self, result):
    nic = ic.InstanceCatalog()
    nic.catalogType = self.filetypes
    ids = []
    ras = []
    decs = []
    magNorms = []
    sedFilenames = []
    Rvs = []
    Avs = []
    eModels = []
    for s in result:
      ids.append(s.Star.id)
      ras.append(s.Star.ra)
      decs.append(s.Star.decl)
      sedFilenames.append(s.Star.sedfilename)
      Rvs.append(3.1)
      Avs.append(s.Star.ebv*Rvs[-1])
      eModels.append('CCM')
      magNorms.append(s.magNorm)
    nic.addColumn(ids, 'id')
    nic.addColumn(ras, 'ra')
    nic.addColumn(decs, 'dec')
    nic.addColumn(magNorms, 'magNorm')
    nic.addColumn(sedFilenames, 'sedFilename')
    nic.addColumn(eModels, 'galacticExtinctionModel')
    nic.addColumn(Avs, 'galacticAv')
    nic.addColumn(Rvs, 'galacticRv')
    nic.metadata = self.metadata
    return nic
