import sys, os, time
import pyoorb
import lsst.sims.catalogs.generation.utils.runTrimCatRRG as rtc
from lsst.sims.catalogs.generation.db import jobDB

def getIds(offset, number, fhids):
  ids = []
  for i,line in enumerate(fhids):
    if i >= offset and i < offset+number:
      flds = line.rstrip().split()
      ids.append(int(flds[0]))
  fhids.close()
  return ids

def run(id, csize=50000, radius=2.1, outdir='./testOut/', repodir='./testRepo/', compress=True, cleanup=False):
    je = jobDB.LogEvents("Test job number %i"%(id), jobid=id)
    print "Job number is %i"%(je._jobid)
    retry = True; nTriesAllowed = 10
    while retry == True and nTriesAllowed > 0:
        retry = False
        try:
            rtc.runTrim(
              csize, id, radius, outdir, repodir, je, compress=compress,
              cleanup=cleanup)
        except Exception, e:
            rtc.writeJobEvent(je, "Exception", description=e.__str__())
            # Wait a long time, then retry
            print '*** Got an exception; sleeping a long time, then retry.'
            time.sleep(30. * 60)
            print 'Woke up and retrying.'
            retry = True
            nTriesAllowed -= 1
            if nTriesAllowed < 1: raise e

if __name__ == "__main__":
  run(int(sys.argv[1]), radius=float(sys.argv[2]), repodir='./testRepo/', csize=55000, cleanup=True)
