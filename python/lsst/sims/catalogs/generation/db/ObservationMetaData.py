import numpy
from .Site import Site
from .observationMetadataUtils import haversine
from .spatialBounds import SpatialBounds

__all__ = ["ObservationMetaData"]

class ObservationMetaData(object):
    """Observation Metadata

    This class contains any metadata for a query which is associated with
    a particular telescope pointing, including bounds in RA and DEC, and
    the time of the observation.

    **Parameters**

        * boundType characterizes the shape of the field of view.  Current options
          are 'box, and 'circle'
        * boundLength is the characteristic length scale of the field of view.
          If boundType is 'box', boundLength can be a float(in which case boundLength is
          half the length of the side of each box) or boundLength can be a numpy array
          in which case the first argument is
          half the width of the RA side of the box and the second argument is half the
          Dec side of the box.
          If boundType is 'circle,' this will be the radius of the circle.
          The bound will be centered on the point (unrefractedRA, unrefractedDec)
        * mjd : float (optional)
          The MJD of the observation
        * epoch : float (optional)
          The epoch of the coordinate system
        * bandpassName : float (optional)
          The canonical name of the bandpass for this observation..
        * phoSimMetadata : dict (optional)
          a dictionary containing metadata used by PhoSim
        * m5: float (optional) or dict (optional)
          the m5 value for either all bands (if a float), or for each band
          in the dict.  This is accessed by the rest of the code through the
          m5(filterName) method.
        * unrefracted[RA,Dec] float (optional)
          The coordinates of the pointing (in degrees)
        * rotSkyPos float (optional)
          The orientation of the telescope (see PhoSim documentation) in degrees.
          This is used by the Astrometry mixins in sims_coordUtils

    **Examples**::
        >>> if you want box_bounds = dict(ra_min=0.0, ra_max=10.0, dec_min=10.0, dec_max=20.0)
        >>> data = ObservationMetaData(boundType='box', unrefractedRA=5.0, unrefractedDec=15.0,
                    boundLength=5.0)

    """

    def __init__(self, boundType=None, boundLength=None,
                 mjd=None, unrefractedRA=None, unrefractedDec=None, rotSkyPos=0.0,
                 bandpassName='r', phoSimMetadata=None, site=None, m5=None):

        self.bounds = None
        self.boundType = boundType
        self.boundLength = boundLength
        self.mjd = mjd
        self.bandpass = bandpassName
        self.unrefractedRA = unrefractedRA
        self.unrefractedDec = unrefractedDec
        self.rotSkyPos = rotSkyPos

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

