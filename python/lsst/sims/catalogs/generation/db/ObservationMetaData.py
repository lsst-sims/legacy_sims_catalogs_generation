from .Site import Site

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
        * metadata : dict (optional)
          a dictionary containing arbitrary metadata

    **Examples**::

        >>> data = ObservationMetaData(dict(('ra_min', 0), ('ra_max', 10), ('dec_min', 10), ('dec_max', 20)))

    """
            
    def __init__(self, circ_bounds=None, box_bounds=None, 
                 mjd=None, UnrefractedRA=None, UnrefractedDec=None, RotSkyPos=None,
                 bandpassName=None, phoSimMetadata={}, site=None):
                 
        if circ_bounds is not None and box_bounds is not None:
            raise ValueError("Passing both circ_bounds and box_bounds")
        self.circ_bounds = circ_bounds
        self.box_bounds = box_bounds
        self.mjd = mjd
        self.bandpass = bandpassName
        self.UnrefractedRA = UnrefractedRA
        self.UnrefractedDec = UnrefractedDec
        self.RotSkyPos = RotSkyPos

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

        if 'Opsim_expmjd' in self.phoSimMetadata:
            self.mjd = phoSimMetadata['Opsim_expmjd'][0]
        
        if 'Unrefracted_RA' in self.phoSimMetadata:
            self.UnrefractedRA = self.phoSimMetadata['Unrefracted_RA'][0]

        if 'Opsim_rotskypos' in self.phoSimMetadata:
            self.RotSkyPos = self.phoSimMetadata['Opsim_rotskypos'][0]
        
        if 'Unrefracted_Dec' in self.phoSimMetadata:
            self.UnrefractedDec = self.phoSimMetadata['Unrefracted_Dec'][0]
        
        if 'Opsim_filter' in self.phoSimMetadata:
            self.bandpass = self.phoSimMetadata['Opsim_filter'][0]
