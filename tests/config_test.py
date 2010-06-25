import unittest, os
from lsst.sims.catalogs.generation.config import ConfigObj

class ConfigObjTest(unittest.TestCase):
    """ unit tests for reading config files """
    def testMetadata(self):
        config = ConfigObj("testMetadata.dat")
        self.assertEqual(config['TRIM']['SIM_SEED'][0],'long')
        self.assertEqual(config['TRIM']['SIM_SEED'][1],'expdate')
    def testSchemaData(self):
        config = ConfigObj("testSchemaData.dat")
        self.assertEqual(config['TRIM']['GALACTIC']['POINT']['id'][1],'id')
        self.assertEqual(config['TRIM']['EXTRAGALACTIC']['SERSIC2D']['magNorm'][0],'float')
if __name__ == '__main__':
    unittest.main()
