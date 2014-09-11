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
                 bandpassName=None, metadata={}, site=None):
                 
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
        
        if metadata is not None:
            self.assignMetaData(metadata)    
        else:
            self.metadata = None
        
    def assignMetaData(self, metaData):
        """
        Assign the dict metaData to be the associated metadata dict of this object
        """
        
        self.metadata = metaData

        if self.mjd is None and 'Opsim_expmjd' in self.metadata:
            self.mjd = metadata['Opsim_expmjd'][0]
        
        if self.UnrefractedRA is None and 'Unrefracted_RA' in self.metadata:
            self.UnrefractedRA = self.metadata['Unrefracted_RA'][0]

        if self.RotSkyPos is None and 'Opsim_rotskypos' in self.metadata:
            self.RotSkyPos = self.metadata['Opsim_rotskypos'][0]
        
        if self.UnrefractedDec is None and 'Unrefracted_Dec' in self.metadata:
            self.UnrefractedDec = self.metadata['Unrefracted_Dec'][0]
        
        if self.bandpass is None and 'Opsim_filter' in self.metadata:
            self.bandpass = self.metadata['Opsim_filter'][0]
