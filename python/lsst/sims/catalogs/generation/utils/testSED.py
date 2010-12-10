# execfile('testSED.py')

import os, sys

inFile = '/share/athena/share/sdata1/rgibson/jobAllocator/trimanon_86_TRIM.ja'
sEDDir = '/share/pogo3/krughoff/raytrace_data/'

doneFiles = []
f = open(inFile, 'r')
fOut = open('testSED.dat', 'w')
for line in f:
    if not line.startswith('object'): continue
    t0 = line.split()
    sED = t0[5]
    t1 = sED.split('/')
    if t1[1] in doneFiles: continue
    print t1[1]
    if t1[1].startswith('k'): path0 = 'starSED/kurucz/'
    elif t1[1].startswith('m'): path0 = 'starSED/mlt/'
    elif t1[1].startswith('l'): path0 = 'starSED/mlt/'
    elif t1[1].startswith('t'): path0 = 'starSED/mlt/'
    elif t1[1].startswith('bergeron'): path0 = 'starSED/wDs/'
    elif t1[1].startswith('Burst') or t1[1].startswith('Inst') or \
         t1[1].startswith('Exp') or t1[1].startswith('Const'):
        path0 = 'galaxySED/'
    elif t1[1] == 'C.dat' or t1[1] == 'S.dat': path0 = 'ssmSED/'
    else: raise ValueError, '*** Uknown SED: %s' % sED

    t2 = sEDDir + path0 + t1[1]
    if not os.path.exists(t2):
        raise ValueError, '*** Could not find SED: %s' % sED
    fOut.write('%s %s\n' % (t1[1], path0 + t1[1]))
    doneFiles.append(t1[1])

f.close()
fOut.close()
