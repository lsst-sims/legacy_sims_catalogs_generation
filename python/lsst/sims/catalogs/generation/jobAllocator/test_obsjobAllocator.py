import os, sys
import jobAllocator

print 'testFullTrimCatalog()'
if os.path.exists('/local/tmp/'):
    workDir = '/local/tmp/jobAllocator/'
elif os.path.exists('/share/athena/share/sdata1/rgibson/'):
    workDir = '/share/athena/share/sdata1/rgibson/jobAllocator/'
else:
    raise RuntimeError, '*** No place for workDir.'
j = jobAllocator.JobAllocator(workDir=workDir, chunkSize=500000, maxCats=-1)
# For some reason, need to use square brackets
j.startCatalogs(['TRIM'], ['ALLSTARS', 'GLENS', 'IMAGE', 'EASTEREGGS', 'SSM', 'GALAXY_DISK', 'GALAXY_BULGE', 'AGN'], sys.argv[1])
