#!/usr/bin/env python
import numpy
from numpy import random
import pyfits
import math
from copy import deepcopy
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
    #open fits file and get the data from the first non-primary extension
    hdulist = pyfits.open(file)
    data = hdulist[1].data
    hdulist.close()
    #list of attributes for the lens table
    lensAttList = ["ra", "decl", "id", "ra_bulge", "dec_bulge", "redshift", "b_bulge",
            "a_bulge", "pa_bulge", "sedname_bulge", "magnorm_bulge", "fluxnorm_bulge", 
            "ext_model_bulge", "rv_bulge", "av_bulge", "u", "g", "r", "i",
            "z", "y"]
    lensList = {}
    #initialize each key to an empty array
    for la in lensAttList:
      lensList[la] = []
    #list of attributes for the image table
    imgAttList = ["lensid", "imgid", "nimg", "ra", "decl", "u", "g", "r",
            "i", "z", "y", "sedname", "redshift", "t_0",
            "magnorm", "fluxnorm", "absimag", "sfinf", "tau", "extmodel", "rv", "av"]
    imgList = {}
    #initialize each key to an empty array
    for ia in imgAttList:
      imgList[ia] = []
    #read through data and positions in lock step
    for l in zip(data, self.centpos):
      print l[0].row
      #get data row
      larr = l[0].array[l[0].row]
      #get position array [ra, dec]
      lpos = l[1]
      #Assign positions, id, and redshift to appropriate keys
      lensList['ra'].append(lpos[0])
      lensList['decl'].append(lpos[1])
      lensList['ra_bulge'].append(lpos[0])
      lensList['dec_bulge'].append(lpos[1])
      lensList['id'].append(int(larr['lensid']))
      lensList['redshift'].append(larr['zlens'])
      #Assign spacial attributes and sed
      lensList['b_bulge'].append(larr['reff_t']*numpy.sqrt(1.0 - larr['ellip']))
      lensList['a_bulge'].append(larr['reff_t']/numpy.sqrt(1.0 - larr['ellip']))
      lensList['pa_bulge'].append(larr['phie'])
      lensList['sedname_bulge'].append("Exp.50E09.1Z.spec")
      #Calculate flux normalization constants used by the raytrace
      lensList['i'].append(larr['apmag_i'])
      (magnorm, fluxnorm) = self.calcMagNorm("galaxySED/"+lensList['sedname_bulge'][-1],
              lensList['i'][-1], lensList['redshift'][-1])
      lensList['magnorm_bulge'].append(magnorm)
      lensList['fluxnorm_bulge'].append(fluxnorm)
      #Calculate LSST magnitude for reference
      mags = self.calcLSSTMags("galaxySED/"+lensList['sedname_bulge'][-1],
              fluxnorm, lensList['redshift'][-1])
      #Test magnitude generation and assign magnitudes to keys
      if not numpy.fabs(lensList['i'][-1] - mags['i']) < 0.00001:
        raise "Something is wrong with the lens mag calculations %.14f %.14f"%(lensList['imag'][-1], mags['i'])
      lensList['u'].append(mags['u'])
      lensList['g'].append(mags['g'])
      lensList['r'].append(mags['r'])
      lensList['z'].append(mags['z'])
      lensList['y'].append(mags['y'])
      #Fill in default info for the lens intrinsic extinction
      lensList['ext_model_bulge'].append("CCM")
      lensList['rv_bulge'].append(3.1)
      lensList['av_bulge'].append(0.0)
      #Set values used by all images 
      nimg = larr['nimg']
      sourceMag = larr['magi_in']
      sourceSpec = "agn.spec"
      sourceRedshift = larr['zsrc']
      #Calculate absolute magnitude of the source from the luminosity
      #distance, spectrum, apparent magnitude in i and the redshift
      sourceAbsMag = self.calcAbsMag(sourceMag, larr['dslum'], "agnSED/"+sourceSpec, sourceRedshift)
      #Calculate QSO variability parameters
      (tau, sfu, sfg, sfr, sfi, sfz, sfy) = self.getSFTau(sourceAbsMag, sourceRedshift)
      for i in range(nimg):
        #Assign position, spectrum, ids etc
        imgList['nimg'].append(nimg)
        imgList['lensid'].append(larr['lensid'])
        imgList['imgid'].append(i)
        imgList['i'].append(sourceMag - 2.5*numpy.log10(numpy.abs(larr['mag'][i])))
        imgList['sedname'].append(sourceSpec)
        imgList['redshift'].append(sourceRedshift)
        imgList['sfinf'].append(sfr)
        imgList['tau'].append(tau)
        imgList['ra'].append(lensList['ra'][-1] -
                larr['ximg'][i]*sec2deg/numpy.cos(lensList['decl'][-1]*deg2rad))
        imgList['decl'].append(lensList['decl'][-1] + larr['yimg'][i]*sec2deg)
        imgList['t_0'].append(larr['delay'][i])
        #Calculate flux normalization and magnitueds for each image
        (magnorm, fluxnorm) = self.calcMagNorm("agnSED/"+imgList['sedname'][-1],
                imgList['i'][-1], imgList['redshift'][-1])
        imgList['magnorm'].append(magnorm)
        imgList['fluxnorm'].append(fluxnorm)
        imgList['absimag'].append(sourceAbsMag)
        mags = self.calcLSSTMags("agnSED/"+sourceSpec, fluxnorm, sourceRedshift)
        #Test magnitude generation.
        if not numpy.fabs(imgList['i'][-1] - mags['i']) < 0.00001:
          raise "Something is wrong with the image mag calculations %.14f %.14f"%(imgList['i'][-1], mags['i'])
        imgList['u'].append(mags['u'])
        imgList['g'].append(mags['g'])
        imgList['r'].append(mags['r'])
        imgList['z'].append(mags['z'])
        imgList['y'].append(mags['y'])
        #Assign default host extinction parameters for source
        imgList['extmodel'].append("CCM")
        imgList['rv'].append(3.1)
        imgList['av'].append(0.0)
    return lensList, imgList
    
  def readPositionFile(self, file):
    """ reads the positions from a two column file assuming ra, dec """
    centra = []
    centdec = []
    fh = open(file)
    for l in fh:
      pos = [float(el) for el in l.rstrip().split()]      
      centra.append(pos[0]%360.)
      centdec.append(pos[1])
    return zip(centra,centdec)
     
  def calcMagNorm(self, spec, mag, redshift, filter='i'):
    """Calculate the SED normalization given a spectrum, redshift, and
    reference magnitude.  ***This assumes not host redenning.***
    """
    #Set paths to default throughputs and seds
    tpath = os.getenv('LSST_THROUGHPUTS_DEFAULT')
    spath = os.getenv('SED_DATA')
    #Setup the filters
    band = Bandpass()
    band.readThroughput(os.path.join(tpath,"total_%s.dat"%(filter)))
    imsimband = Bandpass()
    imsimband.imsimBandpass()
    #setup the sed
    sed = Sed()
    sed.readSED_flambda(os.path.join(spath,spec))
    #need the rest frame spectrum for calculating the mag norm since
    #the normalization is applied in the rest frame
    sed_orig = deepcopy(sed)
    #Redshift the spectrum
    sed.redshiftSED(redshift, dimming=True)
    #Calculate the normalization using the reference magnitude
    fluxNorm = sed.calcFluxNorm(mag, band)
    sed_orig.multiplyFluxNorm(fluxNorm)
    #Calculate the normalization in units of magnitudes
    magNorm = sed_orig.calcMag(imsimband)
    return magNorm, fluxNorm

  def calcLSSTMags(self, spec, fluxnorm, redshift):
    """Calculate the magnitude of the source given a flux normalization in the
    standard LSST bands.  ***This does not take into account host extinction.
    """
    #Get default sed and filter locations
    tpath = os.getenv('LSST_THROUGHPUTS_DEFAULT')
    spath = os.getenv('SED_DATA')
    #setup and redshift the spectrum
    sed = Sed()
    sed.readSED_flambda(os.path.join(spath,spec))
    sed.multiplyFluxNorm(fluxnorm)
    sed.redshiftSED(redshift, dimming=True)
    bands = {"u":None, "g":None, "r":None, "i":None, "z":None, "y":None}
    mags = {"u":None, "g":None, "r":None, "i":None, "z":None, "y":None}
    keys = bands.keys()
    #Calculate the magnitudes for each band
    for k in keys:
      bands[k] = Bandpass()
      bands[k].readThroughput(os.path.join(tpath, "total_%s.dat"%k))
      mags[k] = sed.calcMag(bands[k])
    return mags
    
  def calcAbsMag(self, mag, D_L, spec, redshift, filter='i'):
    """Calculate an absolute magnitude given a filter, luminosity distance,
    apparent magnitude, sed, and redshift
    """
    #Get default locations for filters and seds
    tpath = os.getenv('LSST_THROUGHPUTS_DEFAULT')
    spath = os.getenv('SED_DATA')
    #Set up filters and sed
    band = Bandpass()
    band.readThroughput(os.path.join(tpath,"total_%s.dat"%filter))
    imsimband = Bandpass()
    imsimband.imsimBandpass()
    sed = Sed()
    sed.readSED_flambda(os.path.join(spath,spec))
    #Calculate rest frame magnitude
    magr = sed.calcMag(band)
    #redshift spectrum
    sed.redshiftSED(redshift, dimming=False)
    #calculate observed frame magnitude
    mago = sed.calcMag(band)
    #SED portion of the K-correction
    Kcorr = mago-magr
    #Cosmological portion of the K-correction due to the dilation of the
    #filter
    Kcorrz = 2.5*numpy.log10(1+redshift)
    #D_L is in Mpc so the normal relation goes 5.(log(D_L) +6.-1.)
    absMag = mag - (5.*(numpy.log10(D_L) + 5.)) - Kcorr - Kcorrz
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
    lamRFu = 3700. / (1.+redshift)
    lamRFg = 4800. / (1.+redshift)
    lamRFr = 6200. / (1.+redshift)
    lamRFi = 7600. / (1.+redshift)
    lamRFz = 8800. / (1.+redshift)
    lamRFy = 10100. / (1.+redshift)

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
