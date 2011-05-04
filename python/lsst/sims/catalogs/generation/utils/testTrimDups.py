# execfile('testTrimDups.py')

import os, sys, gzip

trimFile = sys.argv[1]
oIDs = {} 
trimLine = -1
if trimFile.endswith('gz'): f = gzip.open(trimFile, 'r')
else: f = open(trimFile, 'r')
for line in f:
    trimLine += 1
    if trimLine % 10000 == 0: print '   Line:', trimLine
    if not line.startswith('object'): continue
    t0 = line.split()
    if oIDs.has_key(t0[1]):
        raise RuntimeError, '*** Duplicate entry: %s' % t0[1]
    oIDs[t0[1]] = 1

f.close()
print 'No duplicates found.'

