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
        * m5: float (optional) or dict (optional)
          the m5 value for either all bands (if a float), or for each band
          in the dict.  This is accessed by the rest of the code through the
          m5(filterName) method.

    **Examples**::

        >>> data = ObservationMetaData(dict(('ra_min', 0), ('ra_max', 10), ('dec_min', 10), ('dec_max', 20)))

    """
            
    def __init__(self, circ_bounds=None, box_bounds=None, mjd=None, bandpassName=None, 
                 m5 = None, metadata=None):
                 
        if circ_bounds is not None and box_bounds is not None:
            raise ValueError("Passing both circ_bounds and box_bounds")
        self.circ_bounds = circ_bounds
        self.box_bounds = box_bounds
        self.mjd = mjd
        self.bandpass = bandpassName
        self.metadata = metadata
        
        if m5 is None:
            self.m5value = {}
        elif isinstance(m5, dict) or isinstance(m5, float):
            self.m5value = m5
        else:
            raise ValueError("You passed neither a dict nor a float as m5 to ObservationMetaData")

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
