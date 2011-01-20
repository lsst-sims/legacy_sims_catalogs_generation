#!/usr/bin/env python
import numpy
from numpy import random
import pyfits
import math
from copy import copy
import os
from lsst.sims.catalogs.generation.config import ConfigObj
from lsst.sims.catalogs.measures.photometry.Bandpass import *
from lsst.sims.catalogs.measures.photometry.Sed import *

class LensIngester (object):
  def __init__(self, file, posfile):
    #Read the data file.  This will presumably need to be specific to the data
    self.centpos = self.readPositionFile(posfile) 
    (self.lensData, self.imgData) = self.readFile(file)
 
    
  def readFile(self, file):
    sec2deg = 1./60.
    deg2rad = math.pi/180.
    hdulist = pyfits.open(file)
    data = hdulist[1].data
    hdulist.close()
    lensAttList = ["ra", "decl", "id", "ra_bulge", "dec_bulge", "redshift", "b_bulge",
            "a_bulge", "pa_bulge", "sedname_bulge", "magnorm_bulge", "fluxnorm_bulge", 
            "ext_model_bulge", "rv_bulge", "av_bulge", "u", "g", "r", "i",
            "z", "y"]
    lensList = {}
    for la in lensAttList:
      lensList[la] = []
    imgAttList = ["lensid", "imgid", "nimg", "ra", "decl", "u", "g", "r",
            "i", "z", "y", "sedname", "redshift", "t_0",
            "magnorm", "fluxnorm", "absimag", "sfinf", "tau", "extmodel", "rv", "av"]
    imgList = {}
    for ia in imgAttList:
      imgList[ia] = []
    for l in zip(data, self.centpos):
      print l[0].row
      larr = l[0].array[l[0].row]
      lpos = l[1]
      lensList['ra'].append(lpos[0])
      lensList['decl'].append(lpos[1])
      lensList['ra_bulge'].append(lpos[0])
      lensList['dec_bulge'].append(lpos[1])
      lensList['id'].append(int(larr['lensid']))
      lensList['redshift'].append(larr['zlens'])
      lensList['b_bulge'].append(larr['reff_t']*numpy.sqrt(1.0 - larr['ellip']))
      lensList['a_bulge'].append(larr['reff_t']/numpy.sqrt(1.0 - larr['ellip']))
      lensList['pa_bulge'].append(larr['phie'])
      lensList['sedname_bulge'].append("Exp.50E09.1Z.spec")
      lensList['i'].append(larr['apmag_i'])
      (magnorm, fluxnorm) = self.calcMagNorm("galaxySED/"+lensList['sedname_bulge'][-1],
              lensList['i'][-1], lensList['redshift'][-1])
      lensList['magnorm_bulge'].append(magnorm)
      lensList['fluxnorm_bulge'].append(fluxnorm)
      mags = self.calcLSSTMags("galaxySED/"+lensList['sedname_bulge'][-1],
              fluxnorm, lensList['redshift'][-1])
      if not numpy.fabs(lensList['i'][-1] - mags['i']) < 0.00001:
        raise "Something is wrong with the lens mag calculations %.14f %.14f"%(lensList['imag'][-1], mags['i'])
      lensList['u'].append(mags['u'])
      lensList['g'].append(mags['g'])
      lensList['r'].append(mags['r'])
      lensList['z'].append(mags['z'])
      lensList['y'].append(mags['y'])
      lensList['ext_model_bulge'].append("CCM")
      lensList['rv_bulge'].append(3.1)
      lensList['av_bulge'].append(0.0)
      nimg = larr['nimg']
      sourceMag = larr['magi_in']
      sourceSpec = "agn.spec"
      sourceRedshift = larr['zsrc']
      sourceAbsMag = self.calcAbsMag(sourceMag, larr['dslum'], "agnSED/"+sourceSpec, sourceRedshift)
      (tau, sfu, sfg, sfr, sfi, sfz, sfy) = self.getSFTau(sourceAbsMag, sourceRedshift)
      for i in range(nimg):
        imgList['nimg'].append(nimg)
        imgList['lensid'].append(larr['lensid'])
        imgList['imgid'].append(i)
        imgList['imag'].append(sourceMag - 2.5*numpy.log10(numpy.abs(larr['mag'][i])))
        imgList['specname'].append(sourceSpec)
        imgList['redshift'].append(sourceRedshift)
        imgList['ra'].append(lensList['ra'][-1] -
                larr['ximg'][i]*sec2deg/numpy.cos(lensList['decl'][-1]*deg2rad))
        imgList['decl'].append(lensList['decl'][-1] + larr['yimg'][i]*sec2deg)
        imgList['t_0'].append(larr['delay'][i])
        (magnorm, fluxnorm) = self.calcMagNorm("agnSED/"+imgList['specname'][-1],
                imgList['imag'][-1], imgList['redshift'][-1])
        imgList['magnorm'].append(magnorm)
        imgList['fluxnorm'].append(fluxnorm)
        imgList['absimag'].append(sourceAbsMag)
        imgList['extmodel'].append("CCM")
        imgList['rv'].append(3.1)
        imgList['av'].append(0.0)
        imgList['sfinf'].append(sfr)
        imgList['tau'].append(tau)
        mags = self.calcLSSTMags("agnSED/"+sourceSpec, fluxnorm, sourceRedshift)
        if not numpy.fabs(imgList['imag'][-1] - mags['i']) < 0.00001:
          raise "Something is wrong with the image mag calculations %.14f %.14f"%(imgList['imag'][-1], mags['i'])
        imgList['umag'].append(mags['u'])
        imgList['gmag'].append(mags['g'])
        imgList['rmag'].append(mags['r'])
        imgList['zmag'].append(mags['z'])
        imgList['ymag'].append(mags['y'])
    return lensList, imgList
    
  def readPositionFile(self, file):
    centra = []
    centdec = []
    fh = open(file)
    for l in fh:
      pos = [float(el) for el in l.rstrip().split()]      
      centra.append(pos[0]%360.)
      centdec.append(pos[1])
    return zip(centra,centdec)
     
  def calcMagNorm(self, spec, mag, redshift):
    tpath = os.getenv('LSST_THROUGHPUTS_DEFAULT')
    spath = os.getenv('SED_DATA')
    iband = Bandpass()
    iband.readThroughput(os.path.join(tpath,"total_i.dat"))
    imsimband = Bandpass()
    imsimband.imsimBandpass()
    sed = Sed()
    sed.readSED_flambda(os.path.join(spath,spec))
    sed_orig = copy(sed)
    sed.redshiftSED(redshift, dimming=True)
    fluxNorm = sed.calcFluxNorm(mag, iband)
    sed_orig.multiplyFluxNorm(fluxNorm)
    magNorm = sed_orig.calcMag(imsimband)
    return magNorm, fluxNorm

  def calcLSSTMags(self, spec, fluxnorm, redshift):
    tpath = os.getenv('LSST_THROUGHPUTS_DEFAULT')
    spath = os.getenv('SED_DATA')
    sed = Sed()
    sed.readSED_flambda(os.path.join(spath,spec))
    sed.multiplyFluxNorm(fluxnorm)
    sed.redshiftSED(redshift, dimming=True)
    bands = {"u":None, "g":None, "r":None, "i":None, "z":None, "y":None}
    mags = {"u":None, "g":None, "r":None, "i":None, "z":None, "y":None}
    keys = bands.keys()
    for k in keys:
      bands[k] = Bandpass()
      bands[k].readThroughput(os.path.join(tpath, "total_%s.dat"%k))
      mags[k] = sed.calcMag(bands[k])
    return mags
    
  def calcAbsMag(self, mag, D_L, spec, redshift):
    tpath = os.getenv('LSST_THROUGHPUTS_DEFAULT')
    spath = os.getenv('SED_DATA')
    iband = Bandpass()
    iband.readThroughput(os.path.join(tpath,"total_i.dat"))
    imsimband = Bandpass()
    imsimband.imsimBandpass()
    sed = Sed()
    sed.readSED_flambda(os.path.join(spath,spec))
    mago = sed.calcMag(iband)
    sed.redshiftSED(redshift, dimming=False)
    magr = sed.calcMag(iband)
    Kcorr = mago-magr
    Kcorrz = 2.5*numpy.log10(1+redshift)
    #D_L is in Mpc so the normal relation goes 5.(log(D_L) +6.-1.)
    absMag = mag - (5.*(numpy.log10(D_L) + 5.)) + Kcorr - Kcorrz
    return absMag

  def getSFTau(self, absmagi, redshift):
    ## given redshift and Mi (rest-frame),
    ## compute tau (days) at 4000 Ang (rest-frame) and
    ## SFinf at ugrizy in ***observer's frame***

    ## model for black hole
    logMbh9 = 2.4 - 0.25*absmagi - 9.
    ## and sigma is 0.5 dex
    logMbh9 += random.normal(0.0, 0.5)

    ### tau model
    # logTau = 2.34 +0.47*log(lamRF/4000) -0.021*(Mi+23) + 0.12*logMbh9
    logTau = 2.34 -0.021*(absmagi+23) + 0.12*logMbh9

    ## sigma is 0.3 dex for tau
    logTau += random.normal(0.0, 0.3)
    tau = 10**(logTau)

    ### SFinf model
    # logSF = -0.55 -0.47*log(lamRF/4000) +0.11*(Mi+23) + 0.11*logMbh9
    SFinf4000 = -0.55 +0.11*(absmagi+23.) + 0.11*logMbh9

    # and now compute at every *observed* wavelength
    lamRFu = 3700 / (1+redshift)
    lamRFg = 4800 / (1+redshift)
    lamRFr = 6200 / (1+redshift)
    lamRFi = 7600 / (1+redshift)
    lamRFz = 8800 / (1+redshift)
    lamRFy = 10100 / (1+redshift)

    SF0 = 10**(SFinf4000)
    SFu = SF0 * (lamRFu/4000.)**(-0.47)
    SFg = SF0 * (lamRFg/4000.)**(-0.47)
    SFr = SF0 * (lamRFr/4000.)**(-0.47)
    SFi = SF0 * (lamRFi/4000.)**(-0.47)
    SFz = SF0 * (lamRFz/4000.)**(-0.47)
    SFy = SF0 * (lamRFy/4000.)**(-0.47)
    return tau, SFu, SFg, SFr, SFi, SFz, SFy

  def writeLensData(self, file):
    fh = open(file, "w")
    keys = self.lensData.keys()
    fh.write(",".join(keys)+"\n")
    zipex = "zip(%s)"%(",".join(["self.lensData['%s']"%k for k in keys]))
    for arr in eval(zipex):
      fh.write(",".join([str(el) for el in arr])+"\n")
    fh.close()

  def writeImgData(self, file):
    fh = open(file, "w")
    keys = self.imgData.keys()
    fh.write(",".join(keys)+"\n")
    zipex = "zip(%s)"%(",".join(["self.imgData['%s']"%k for k in keys]))
    for arr in eval(zipex):
      fh.write(",".join([str(el) for el in arr])+"\n")
    fh.close()
    
if __name__ == "__main__":
  li = LensIngester("oguri_qso_LSST_fstar.fits", "Basic_15x15_skygrid_PT1.2_radec.txt")
  li.writeLensData("lens.csv")
  li.writeImgData("image.csv")
