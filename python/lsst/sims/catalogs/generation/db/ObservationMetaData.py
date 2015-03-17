import numpy
from .spatialBounds import SpatialBounds
from lsst.sims.utils import haversine, Site

__all__ = ["ObservationMetaData"]

class ObservationMetaData(object):
    """Observation Metadata

    This class contains any metadata for a query which is associated with
    a particular telescope pointing, including bounds in RA and DEC, and
    the time of the observation.

    **Parameters**

        * unrefracted[RA,Dec] float
          The coordinates of the pointing (in degrees)

        * boundType characterizes the shape of the field of view.  Current options
          are 'box, and 'circle'

        * boundLength is the characteristic length scale of the field of view in degrees.
          If boundType is 'box', boundLength can be a float(in which case boundLength is
          half the length of the side of each box) or boundLength can be a numpy array
          in which case the first argument is
          half the width of the RA side of the box and the second argument is half the
          Dec side of the box.
          If boundType is 'circle,' this will be the radius of the circle.
          The bound will be centered on the point (unrefractedRA, unrefractedDec)

        * mjd : float (optional)
          The MJD of the observation

        * bandpassName : float (optional)
          The canonical name of the bandpass for this observation.

        * phoSimMetadata : dict (optional)
          a dictionary containing metadata used by PhoSim

        * m5: float (optional) or dict (optional)
          the m5 value for either all bands (if a float), or for each band
          in the dict.  This is accessed by the rest of the code through the
          m5(filterName) method.

        * skyBrightness: float (optional) the magnitude of the sky in the
          filter specified by bandpassName

        * rotSkyPos float (optional)
          The orientation of the telescope (see PhoSim documentation) in degrees.
          This is used by the Astrometry mixins in sims_coordUtils

    **Examples**::
        >>> data = ObservationMetaData(boundType='box', unrefractedRA=5.0, unrefractedDec=15.0,
                    boundLength=5.0)

    """

    def __init__(self, boundType=None, boundLength=None,
                 mjd=None, unrefractedRA=None, unrefractedDec=None, rotSkyPos=0.0,
                 bandpassName='r', phoSimMetadata=None, site=None, m5=None, skyBrightness=None):

        self.bounds = None
        self.boundType = boundType
        self.mjd = mjd
        self.bandpass = bandpassName
        self.skyBrightness = skyBrightness

        if rotSkyPos is not None:
            self.rotSkyPos = numpy.radians(rotSkyPos)
        else:
            self.rotSkyPos = None

        if unrefractedRA is not None:
            self.unrefractedRA = numpy.radians(unrefractedRA)
        else:
            self.unrefractedRA = None

        if unrefractedDec is not None:
            self.unrefractedDec = numpy.radians(unrefractedDec)
        else:
            self.unrefractedDec = None

        if boundLength is not None:
            if isinstance(boundLength, float):
                self.boundLength = numpy.radians(boundLength)
            else:
                try:
                    self.boundLength = []
                    for ll in boundLength:
                        self.boundLength.append(numpy.radians(ll))
                except:
                    raise RuntimeError("You seem to have passed something that is neither a float nor " +
                                       "list-like as boundLength to ObservationMetaData")
        else:
            self.boundLength = None

        if site is not None:
            self.site=site
        else:
            self.site=Site()

        if m5 is None or isinstance(m5, dict) or isinstance(m5, float):
            self.m5value = m5
        else:
            raise ValueError("You passed neither a dict nor a float as m5 to ObservationMetaData")

        if site is not None:
            self.site=site
        else:
            self.site=Site()

        if phoSimMetadata is not None:
            self.assignPhoSimMetaData(phoSimMetadata)
        else:
            self.phoSimMetadata = None

        #this should be done after phoSimMetadata is assigned, just in case
        #assignPhoSimMetadata overwrites unrefractedRA/Dec
        if self.bounds is None:
            self.buildBounds()
            

    @property
    def summary(self):
        mydict = {}
        mydict['site'] = self.site

        mydict['boundType'] = self.boundType
        mydict['boundLength'] = self.boundLength
        mydict['unrefractedRA'] = self.unrefractedRA
        mydict['unrefractedDec'] = self.unrefractedDec
        mydict['rotSkyPos'] = self.rotSkyPos

        mydict['mjd'] = self.mjd
        mydict['bandpass'] = self.bandpass
        mydict['skyBrightness'] = self.skyBrightness
        # mydict['m5'] = self.m5

        mydict['phoSimMetadata'] = self.phoSimMetadata

        return mydict


    def buildBounds(self):
        if self.boundType is None:
            return

        if self.boundLength is None:
            raise RuntimeError("ObservationMetadata cannot assign a bounds; it has no boundLength")

        if self.unrefractedRA is None or self.unrefractedDec is None:
            raise RuntimeError("ObservationMetadata cannot assign a bounds; it has no unrefractedRA/Dec")

        self.bounds = SpatialBounds.getSpatialBounds(self.boundType, self.unrefractedRA, self.unrefractedDec,
                                                     self.boundLength)

    def assignPhoSimMetaData(self, metaData):
        """
        Assign the dict metaData to be the associated metadata dict of this object
        """

        self.phoSimMetadata = metaData

        #overwrite member variables with values from the phoSimMetadata
        if self.phoSimMetadata is not None and 'Opsim_expmjd' in self.phoSimMetadata:
            self.mjd = self.phoSimMetadata['Opsim_expmjd'][0]

        if self.phoSimMetadata is not None and 'Unrefracted_RA' in self.phoSimMetadata:
            self.unrefractedRA = self.phoSimMetadata['Unrefracted_RA'][0]

        if self.phoSimMetadata is not None and 'Opsim_rotskypos' in self.phoSimMetadata:
            self.rotSkyPos = self.phoSimMetadata['Opsim_rotskypos'][0]

        if self.phoSimMetadata is not None and 'Unrefracted_Dec' in self.phoSimMetadata:
            self.unrefractedDec = self.phoSimMetadata['Unrefracted_Dec'][0]

        if self.phoSimMetadata is not None and 'Opsim_filter' in self.phoSimMetadata:
            self.bandpass = self.phoSimMetadata['Opsim_filter'][0]

        #in case this method was called after __init__ and unrefractedRA/Dec were
        #overwritten by this method
        if self.bounds is not None:
            self.buildBounds()

    def m5(self,filterName):

       if self.m5value is None:
           raise ValueError("m5 is None in ObservationMetaData")
       elif isinstance(self.m5value,dict):
           if filterName not in self.m5value:
               raise ValueError("Filter %s is not in the m5 dict in ObservationMetaData" % filterName)
           return self.m5value[filterName]
       elif isinstance(self.m5value,float):
           return self.m5value
       else:
           raise ValueError("Somehow, m5 is not set in ObservationMetaData")

