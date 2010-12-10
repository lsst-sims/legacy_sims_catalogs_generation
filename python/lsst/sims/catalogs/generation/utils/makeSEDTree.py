# execfile('testSED.py')

import os, sys

sEDDir = '/astro/net/pogo3/krughoff/raytrace_data/'
subDirs = ['starSED/kurucz/', 'starSED/wDs/', 'starSED/mlt/', 'galaxySED/',
           'ssmSED/' ]

doneFiles = []
fOut = open('makeSEDTree.dat', 'w')

for d in subDirs:
    path0 = d
    t0 = os.listdir(sEDDir + path0)
    for t in t0:
        t1 = '%s %s\n' % (t, path0 + t)
        print t1.rstrip('\n')
        fOut.write(t1)

fOut.close()
