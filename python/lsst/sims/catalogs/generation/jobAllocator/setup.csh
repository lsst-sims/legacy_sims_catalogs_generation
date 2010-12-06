setenv LSST_DEVEL /astro/net/pogo1/dC3b/pT2/lsstsandbox
unsetenv PYTHONPATH
source /astro/apps/lsst_64/loadLSST.csh
setenv CAT_SHARE_DATA /astro/net/lsst1/shared

setup lsst
#eups declare -r /astro/net/pogo1/dC3b/pT2/throughputsSVN throughputs 1.0
setup throughputs
setup -r /astro/users/rgibson/work/sims/catalogs/generation/trunk/
setup -r /astro/users/rgibson/work/sims/catalogs/measures/trunk/


