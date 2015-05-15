import numpy
import inspect
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

        * bandpassName : a char (e.g. 'u') or list (e.g. ['u', 'g', 'z'])
          denoting the bandpasses used for this particular observation

        * phoSimMetaData : dict (optional)
          a dictionary containing metadata used by PhoSim

        * m5: float or list (optional)
          this should be the 5-sigma limiting magnitude in the bandpass or
          bandpasses specified in bandpassName.  Ultimately, m5 will be stored
          in a dict keyed to the bandpassName (or Names) you passed in, i.e.
          you will be able to access m5 from outside of this class using, for
          example:

          myObservationMetaData.m5['u']

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
                 mjd=None, unrefractedRA=None, unrefractedDec=None, rotSkyPos=None,
                 bandpassName=None, phoSimMetaData=None, site=Site(), m5=None, skyBrightness=None):

        self._bounds = None
        self._boundType = boundType
        self._mjd = mjd
        self._bandpass = bandpassName
        self._skyBrightness = skyBrightness
        self._site = site

        if rotSkyPos is not None:
            self._rotSkyPos = numpy.radians(rotSkyPos)
        else:
            self._rotSkyPos = None

        if unrefractedRA is not None:
            self._unrefractedRA = numpy.radians(unrefractedRA)
        else:
            self._unrefractedRA = None

        if unrefractedDec is not None:
            self._unrefractedDec = numpy.radians(unrefractedDec)
        else:
            self._unrefractedDec = None

        if boundLength is not None:
            self._boundLength = numpy.radians(boundLength)
        else:
            self._boundLength = None

        if phoSimMetaData is not None:
            self._assignPhoSimMetaData(phoSimMetaData)
        else:
            self._phoSimMetaData = None

        self._assignM5(m5)

        #this should be done after phoSimMetaData is assigned, just in case
        #self._assignPhoSimMetadata overwrites unrefractedRA/Dec
        if self._bounds is None:
            self._buildBounds()


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

        mydict['phoSimMetaData'] = self.phoSimMetaData

        return mydict

    def _assignM5(self, m5):
        """
        This method sets up the dict self._m5.  It reads in a list of m5 values
        and associates them with the list of bandpass names in self._bandpass.

        Note: this method assumes that self._bandpass has already been set.
        It will raise an exception of self._bandpass is None.

        @param [in] m5 is a list of m5 values corresponding to the bandpasses
        stored in self._bandpass

        This method does not return anything.  It just sets the member variable
        self._m5.
        """

        if m5 is None:
            self._m5 = None
        else:
            bandpassIsList = False
            m5IsList = False

            if self._bandpass is None:
                raise RuntimeError('You cannot set m5 if you have not set bandpass in ObservationMetaData')

            if hasattr(self._bandpass, '__iter__'):
                bandpassIsList = True

            if hasattr(m5, '__iter__'):
                m5IsList = True

            if bandpassIsList and not m5IsList:
                raise RuntimeError('You passed a list of bandpass names' + \
                                   'but did not pass a list of m5s to ObservationMetaData')

            if m5IsList and not bandpassIsList:
                raise RuntimeError('You passed a list of m5s ' + \
                                    'but did not pass a list of bandpass names to ObservationMetaData')


            if m5IsList:
                if len(m5) != len(self._bandpass):
                    raise RuntimeError('The list of m5s you passed to ObservationMetaData ' + \
                                       'has a different length than the list of bandpass names you passed')

            #now build the m5 dict
            if bandpassIsList:
                if len(m5) != len(self._bandpass):
                    raise RuntimeError('In ObservationMetaData you tried to assign bandpass ' +
                                       'and m5 with lists of different length')

                self._m5 = {}
                for b, m in zip(self._bandpass, m5):
                    self._m5[b] = m
            else:
                self._m5 = {self._bandpass:m5}


    def _buildBounds(self):
        """
        Set up the member variable self._bounds.

        If self._boundType, self._boundLength, self._unrefractedRA, or
        self._unrefractedDec are None, nothing will happen.
        """

        if self._boundType is None:
            return

        if self._boundLength is None:
            return

        if self._unrefractedRA is None or self._unrefractedDec is None:
            return

        self._bounds = SpatialBounds.getSpatialBounds(self._boundType, self._unrefractedRA, self._unrefractedDec,
                                                     self._boundLength)

    def _assignPhoSimMetaData(self, metaData):
        """
        Assign the dict metaData to be the associated phoSimMetaData dict of this object.

        In doing so, this method will copy unrefractedRA, unrefractedDec, rotSkyPos,
        MJD, and bandpass from the phoSimMetaData (if present) to the corresponding
        member variables.  If by doing so you try to overwrite a parameter that you
        have already set by hand, this method will raise an exception.
        """

        self._phoSimMetaData = metaData

        #overwrite member variables with values from the phoSimMetaData
        if self._phoSimMetaData is not None and 'Opsim_expmjd' in self._phoSimMetaData:
            if self._mjd is not None:
                raise RuntimeError('WARNING in ObservationMetaData trying to overwrite mjd with phoSimMetaData')

            self._mjd = self._phoSimMetaData['Opsim_expmjd'][0]

        if self._phoSimMetaData is not None and 'Unrefracted_RA' in self._phoSimMetaData:
            if self._unrefractedRA is not None:
                raise RuntimeError('WARNING in ObservationMetaData trying to overwrite unrefractedRA ' +
                                   'with phoSimMetaData')

            self._unrefractedRA = self._phoSimMetaData['Unrefracted_RA'][0]

        if self._phoSimMetaData is not None and 'Opsim_rotskypos' in self._phoSimMetaData:
            if self._rotSkyPos is not None:
                raise RuntimeError('WARNING in ObservationMetaData trying to overwrite rotSkyPos ' +
                                   'with phoSimMetaData')

            self._rotSkyPos = self.phoSimMetaData['Opsim_rotskypos'][0]

        if self._phoSimMetaData is not None and 'Unrefracted_Dec' in self._phoSimMetaData:
            if self._unrefractedDec is not None:
                raise RuntimeError('WARNING in ObservationMetaData trying to overwrite unrefractedDec ' +
                                   'with phoSimMetaData')

            self._unrefractedDec = self._phoSimMetaData['Unrefracted_Dec'][0]

        if self._phoSimMetaData is not None and 'Opsim_filter' in self._phoSimMetaData:
            if self._bandpass is not None:
                raise RuntimeError('WARNING in ObservationMetaData trying to overwrite bandpass ' +
                                   'with phoSimMetaData')

            self._bandpass = self._phoSimMetaData['Opsim_filter'][0]

        self._buildBounds()

    @property
    def unrefractedRA(self):
        """
        The above-the-atmospher RA of the telescope pointing in degrees.
        """
        if self._unrefractedRA is not None:
            return numpy.degrees(self._unrefractedRA)
        else:
            return None

    @unrefractedRA.setter
    def unrefractedRA(self, value):
        if self._phoSimMetaData is not None:
            if 'Unrefracted_RA' in self._phoSimMetaData:
                raise RuntimeError('WARNING overwriting Unrefracted_RA ' +
                                   'which was set by phoSimMetaData')

        self._unrefractedRA = numpy.radians(value)
        self._buildBounds()

    @property
    def unrefractedDec(self):
        """
        The above-the-atmosphere Dec of the telescope pointing in degrees.
        """
        if self._unrefractedDec is not None:
            return numpy.degrees(self._unrefractedDec)
        else:
            return None

    @unrefractedDec.setter
    def unrefractedDec(self, value):
        if self._phoSimMetaData is not None:
            if 'Unrefracted_Dec' in self._phoSimMetaData:
                raise RuntimeError('WARNING overwriting Unrefracted_Dec ' +
                                   'which was set by phoSimMetaData')

        self._unrefractedDec = numpy.radians(value)
        self._buildBounds()

    @property
    def boundLength(self):
        """
        Either a list or a float indicating the size of the field
        of view associated with this ObservationMetaData.

        See the documentation in the SpatialBounds class for more
        details (specifically, the 'length' paramter).

        In degrees (Yes: the documentation in SpatialBounds says that
        the length should be in degrees.  The present class converts
        from degrees to radians before passing to SpatialBounds.
        """
        return numpy.degrees(self._boundLength)

    @boundLength.setter
    def boundLength(self, value):
        self._boundLength = numpy.radians(value)
        self._buildBounds()

    @property
    def boundType(self):
        """
        Tag indicating what sub-class of SpatialBounds should
        be instantiated for this ObservationMetaData.
        """
        return self._boundType

    @boundType.setter
    def boundType(self, value):
        self._boundType = value
        self._buildBounds()

    @property
    def bounds(self):
        """
        Instantiation of a sub-class of SpatialBounds.  This
        is what actually construct the WHERE clause of the SQL
        query associated with this ObservationMetaData.
        """
        return self._bounds

    @property
    def rotSkyPos(self):
        """
        The rotation of the telescope with respect to the sky in degrees.
        It is a parameter you should get from OpSim.
        """
        if self._rotSkyPos is not None:
            return numpy.degrees(self._rotSkyPos)
        else:
            return 0.0

    @rotSkyPos.setter
    def rotSkyPos(self,value):
        if self._phoSimMetaData is not None:
            if 'Opsim_rotskypos' in self._phoSimMetaData:
                raise RuntimeError('WARNING overwriting rotSkyPos ' +
                                   'which was set by phoSimMetaData which was set ' +
                                   'by phoSimMetaData')

        self._rotSkyPos = numpy.radians(value)


    @property
    def m5(self):
        """
        A dict of m5 (the 5-sigma limiting magnitude) values
        associated with the bandpasses represented by this
        ObservationMetaData.
        """
        return self._m5

    @m5.setter
    def m5(self, value):
        self._assignM5(value)

    @property
    def site(self):
        """
        An instantiation of the Site class containing information about
        the telescope site.
        """
        return self._site

    @site.setter
    def site(self, value):
        self._site = value

    @property
    def mjd(self):
        """
        The MJD of the observation associated with this ObservationMetaData.
        """
        return self._mjd

    @mjd.setter
    def mjd(self, value):
        if self._phoSimMetaData is not None:
            if 'Opsim_expmjd' in self._phoSimMetaData:
                raise RuntimeError('WARNING overwriting mjd ' +
                                   'which was set by phoSimMetaData which was set ' +
                                   'by phoSimMetaData')

        self._mjd = value

    @property
    def bandpass(self):
        """
        The bandpass associated with this ObservationMetaData.
        Can be a list.
        """
        if self._bandpass is not None:
            return self._bandpass
        else:
            return 'r'

    def setBandpassAndM5(self, bandpassName=None, m5=None):
        """
        Set the bandpasses and associated 5-sigma limiting magnitudes
        for this ObservationMetaData.

        @param [in] bandpassName is either a char or a list of chars denoting
        the name of the bandpass associated with this ObservationMetaData.

        @param [in] m5 is the 5-sigma-limiting magnitude(s) associated
        with bandpassName

        Nothing is returned.  This method just sets member variables of
        this ObservationMetaData.
        """
        if self._phoSimMetaData is not None:
            if 'Opsim_filter' in self._phoSimMetaData:
                raise RuntimeError('WARNING overwriting bandpass ' +
                                   'which was set by phoSimMetaData which was set ' +
                                   'by phoSimMetaData')

        self._bandpass = bandpassName
        self._assignM5(m5)

    @property
    def skyBrightness(self):
        """
        The sky brightness in mags per square arcsecond associated
        with this ObservationMetaData.
        """
        return self._skyBrightness

    @skyBrightness.setter
    def skyBrightness(self, value):
        self._skyBrightness = value

    @property
    def phoSimMetaData(self):
        """
        A dict of parameters expected by PhoSim characterizing this
        ObservationMetaData.  Note that setting this paramter
        could overwrite unrefractedRA, unrefractedDec, rotSkyPos,
        MJD, or bandpass and m5 (if they are present in this
        dict).
        """
        return self._phoSimMetaData

    @phoSimMetaData.setter
    def phoSimMetaData(self, value):
        if 'Unrefracted_RA' in value:
            self._unrefractedRA = None

        if 'Unrefracted_Dec' in value:
            self._unrefractedDec = None

        if 'Opsim_rotskypos' in value:
            self._rotSkyPos = None

        if 'Opsim_expmjd' in value:
            self._mjd = None

        if 'Opsim_filter' in value:
            self._bandpass = None
            self._m5 = None

        self._assignPhoSimMetaData(value)
