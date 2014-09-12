from .Site import Site
from .observationMetadataUtils import *

class ObservationMetaData(object):
    """Observation Metadata
    
    This class contains any metadata for a query which is associated with
    a particular telescope pointing, including bounds in RA and DEC, and
    the time of the observation.

    **Parameters**

        * circ_bounds : dict (optional)
          a dictionary with the keys 'ra', 'dec', and 'radius' measured, in
          degrees
        * box_bounds : dict (optional)
          a dictionary with the keys 'ra_min', 'ra_max', 'dec_min', 'dec_max',
          measured in degrees
        * mjd : float (optional)
          The MJD of the observation
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

        >>> data = ObservationMetaData(dict(('ra_min', 0), ('ra_max', 10), ('dec_min', 10), ('dec_max', 20)))

    """
            
    def __init__(self, circ_bounds=None, box_bounds=None, 
                 mjd=None, unrefractedRA=None, unrefractedDec=None, rotSkyPos=0.0,
                 bandpassName='r', phoSimMetadata={}, site=None, m5=None):
               
        if circ_bounds is not None and box_bounds is not None:
            raise ValueError("Passing both circ_bounds and box_bounds")
            
        self.circ_bounds = circ_bounds
        self.box_bounds = box_bounds
        self.mjd = mjd
        self.bandpass = bandpassName
        self.unrefractedRA = unrefractedRA
        self.unrefractedDec = unrefractedDec
        self.rotSkyPos = rotSkyPos
       
        if box_bounds is not None:
            #if unrefracted[RA,Dec] is outside of box, set them to the center of the box
            if self.unrefractedRA is None or \
               self.unrefractedDec is None or \
               self.unrefractedRA > box_bounds['ra_max'] or \
               self.unrefractedRA < box_bounds['ra_min'] or \
               self.unrefractedDec < box_bounds['dec_min'] or \
               self.unrefractedDec > box_bounds['dec_max']:
                   
                self.unrefractedRA = 0.5*(box_bounds['ra_max']+box_bounds['ra_min'])
                self.unrefractedDec = 0.5*(box_bounds['dec_max']+box_bounds['dec_min'])    
                
        if circ_bounds is not None:
            #if unfrefracted[RA,Dec] is outside fo the circle, default to the center
            #of the circle (recall that the bounds are all set in degrees)
            
            
            if self.unrefractedRA is None or self.unrefractedDec is None:
                self.unrefractedRA = circ_bounds['ra']
                self.unrefractedDec = circ_bounds['dec']
            else:
                distance = haversine(numpy.radians(self.unrefractedRA),
                                     numpy.radians(self.unrefractedDec),
                                     numpy.radians(circ_bounds['ra']),
                                     numpy.radians(circ_bounds['dec']))
                
                if distance>numpy.radians(circ_bounds['radius']):
                    self.unrefractedRA = circ_bounds['ra']
                    self.unrefractedDec = circ_bounds['dec']
         
        if site is not None:
            self.site=site
        else:
            self.site=Site()

        if m5 is None:
            self.m5value = {}
        elif isinstance(m5, dict) or isinstance(m5, float):
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
        
    def assignPhoSimMetaData(self, metaData):
        """
        Assign the dict metaData to be the associated metadata dict of this object
        """
        
        self.phoSimMetadata = metaData
        
        #overwrite member variables with values from the phoSimMetadata
        if 'Opsim_expmjd' in self.phoSimMetadata:
            self.mjd = self.phoSimMetadata['Opsim_expmjd'][0]
        
        if 'Unrefracted_RA' in self.phoSimMetadata:
            self.unrefractedRA = self.phoSimMetadata['Unrefracted_RA'][0]

        if 'Opsim_rotskypos' in self.phoSimMetadata:
            self.rotSkyPos = self.phoSimMetadata['Opsim_rotskypos'][0]
        
        if 'Unrefracted_Dec' in self.phoSimMetadata:
            self.unrefractedDec = self.phoSimMetadata['Unrefracted_Dec'][0]
        
        if 'Opsim_filter' in self.phoSimMetadata:
            filters = ['u','g','r','i','z','y']
            self.bandpass = filters[self.phoSimMetadata['Opsim_filter'][0]]
               
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
