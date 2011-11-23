#!/usr/bin/env python

"""
This program reads the metadata and catalog files and does sanity checks on
all the constituent files.
"""

def readMetadataFile():
    pass

def readCatalogFile():
    pass

def applyVariability():
    pass

def inspectSpec():
    pass

def compSchema():
    pass

schema['point'] = ['id', 'ra', 'dec', 'umag', 'gmag', 'rmag',\
        'imag', 'zmag', 'ymag', 'specname', 'muRa', 'muDec', 'distance',\
        'doRed']
#We will allow users to either apply zero reddenning or to have us embed the
#object in our dust model.
'''
schema['extended'] = ['id', 'ra', 'dec', 'umag', 'gmag', 'rmag',\
        'imag', 'zmag', 'ymag', 'specname', 'redshift', 'ebv']
This is much harder.  Do we make the users give all information for every
component on one line, or do they need to be one per line.  Do we make them
give us the normalization for each component or do we derive that from
bulge/total or something else?
'''

descriptions = {'id': 'integer identifier per object',\
        'ra': 'Right Ascention in degrees:  May be either absolute or relative',\
        'dec': 'Declination in degrees: May be either absolute or relative',\
        '[ugrizy]mag': 'Apparent redenned magnitude in LSST bands',\
        'specname': 'Name of spectrum -- must be accompalied by at least one magnitude: default None',\
        'muRa/Dec': 'Proper motion in arcsec/yr: default 0',\
        'distance': 'Distance to the object in kpc: default 10',\
        'doRed': 'Redden source with 3D dust model?: default True'}
