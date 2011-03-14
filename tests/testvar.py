import pyoorb
import lsst.sims.catalogs.measures.photometry.Variability as variability
import numpy

def getParams(filename):
    fh = open(filename)
    parr = []
    names = fh.readline().rstrip().split(",")
    for l in fh:
        params = {}
        flds = l.rstrip().split(",")
        for name, fld in zip(names,flds):
            if name == "varMethodName" or name == "filename":
                params[name] = fld
            else:
                params[name] = float(fld)
            parr.append(params)
    return parr

if __name__ == "__main__": 
    startmjd = 50000.
    endmjd = 52000.
    steps = 2000.

    var = variability.Variability(cache=True)
    mjds = numpy.linspace(startmjd, endmjd, steps)
    arr = getParams("agn.dat")
    for a in arr: 
        fhout = open("agn_%i.out"%(a['varsimobjid']),"w")
        dmags = eval("var.%s(a, mjds)"%(a['varMethodName']))
        for i in range(steps):
            line = [mjds[i], dmags['u'][i], dmags['g'][i], dmags['r'][i], dmags['i'][i],\
                    dmags['z'][i], dmags['y'][i]]
            fhout.write(",".join([str(el) for el in line])+"\n")
        fhout.close()

        
    arr = getParams("rrly.dat")
    for a in arr:
        fhout = open("rrly_%i.out"%(a['varsimobjid']),"w")
        dmags = eval("var.%s(a, mjds)"%(a['varMethodName']))
        for i in range(steps):
            line = [mjds[i], dmags['u'][i], dmags['g'][i], dmags['r'][i], dmags['i'][i],\
                    dmags['z'][i], dmags['y'][i]]
            fhout.write(",".join([str(el) for el in line])+"\n")
        fhout.close()


