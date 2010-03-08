#!/usr/bin/env python
from cosmoDBModel import *
from lsst.sims.measurement.instance import instanceCatalog as ic

class queryDB(object):
  def __init__(self, chunksize=100000):
    setup_all()
    self._start=0
    self.chunksize=chunksize
    self.columns = {}
    self.columns['star'] = ('id', 'ra', 'decl')

  def getInstanceCatalogById(self, id, objtype='star', filetypes=("TRIM",), opsim="3_61", add_columns=()):
    os = OpSim3_61.query.filter("obshistid=%i"%(id)).first()
    fscale = schema.Column('flux_scale')
    lcid = schema.Column('isvar')
    t0 = schema.Column('t0')
    obsDate = os.expmjd
    duration = schema.Column('timescale')
    fpeak = schema.Column('varfluxpeak')
    filter = os.filter
    mags  = func.toMag(fscale*func.flux_ratio_from_lc(lcid,t0,obsDate,duration,fpeak,filter)).label('magNorm')
    stars = Star.query.add_column(mags).filter("point @ scircle \'<(%f,%f),%fd>\'"%(os.fieldra, os.fielddec, 2.1)).slice(self._start, self._start+self.chunksize).all()
    
    nic = ic.InstanceCatalog()
    ids = []
    ras = []
    decs = []
    magNorms = []
    sedFilenames = []
    Rvs = []
    Avs = []
    eModels = [] 
    for s in stars:
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
    for k in (os.__dict__.keys()):
      nic.metadata.addMetadata(k,os.__dict__[k],"")
    print nic.metadata.parameters
    return nic
