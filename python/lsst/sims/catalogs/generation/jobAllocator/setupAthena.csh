#unsetenv PYTHONPATH
lsst
setup numpy
setup subversion

setenv CS /share/home/rgibson/catalogs_share
setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:${CS}/postgres.8.4.1/lib:${HOME}/shared

setenv SIMS /share/home/rgibson/sims
setenv CATALOG_DESCRIPTION_PATH ${SIMS}/catalogs/measures/trunk/data/requiredFields/

setenv PYTHONPATH ${PYTHONPATH}:${SIMS}/catalogs/generation/trunk/python/:${SIMS}/catalogs/measures/trunk/python/:$CS/py_mods/lib/python2.5/site-packages/



#setenv LD_LIBRARY_PATH /astro/apps/postgres.8.4.1/lib/:/astro/net/lsst1/shared/
#setenv CATALOG_DESCRIPTION_PATH /astro/users/krughoff/programs/python/catalogs_svn/measures/trunk/data/requiredFields/
#setenv CATALOG_DESCRIPTION_PATH /astro/users/rgibson/work/sims/catalogs/measures/trunk/data/requiredFields/

#setenv PYTHONPATH /astro/apps/lsst_64/Linux64/lssteups/1.0/python:/astro/apps/lsst_64/Linux64/sconsUtils/3.3/python:/astro/apps/lsst_64/Linux64/base/3.1/python:/astro/apps/lsst_64/eups/1.1.0/bin
#setenv PYTHONPATH ${PYTHONPATH}:/astro/users/rgibson/work/sims/catalogs/generation/trunk/python/:/astro/users/rgibson/work/sims/catalogs/measures/trunk/python/

#setenv CATALOG_DESCRIPTION_PATH /astro/users/krughoff/programs/python/catalogs_svn/measures/trunk/data/requiredFields/


