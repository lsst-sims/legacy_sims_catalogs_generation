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
    endmjd = 65000.
    steps = 1500.

    var = variability.Variability(cache=True)
    mjds = numpy.linspace(startmjd, endmjd, steps)
    arr = getParams("agn.dat")
    mag_o = 20.
    for a in arr: 
        fhout = open("agn_%i.out"%(a['varsimobjid']),"w")
        dmags = eval("var.%s(a, mjds)"%(a['varMethodName']))
        fhout.write("#MJD,u,uerr,g,gerr,r,rerr,i,ierr,z,zerr,y,yerr\n")
        for i in range(steps):
            line = [mjds[i], dmags['u'][i]+mag_o, 0.01, dmags['g'][i]+mag_o, 0.01,\
                    dmags['r'][i]+mag_o, 0.01, dmags['i'][i]+mag_o, 0.01,\
                    dmags['z'][i]+mag_o, 0.01, dmags['y'][i]+mag_o, 0.01]
            fhout.write(",".join([str(el) for el in line])+"\n")
        fhout.close()
        mag_o += 0.04

        
    arr = getParams("rrly.dat")
    for a in arr:
        fhout = open("rrly_%i.out"%(a['varsimobjid']),"w")
        dmags = eval("var.%s(a, mjds)"%(a['varMethodName']))
        for i in range(steps):
            line = [mjds[i], dmags['u'][i], dmags['g'][i], dmags['r'][i], dmags['i'][i],\
                    dmags['z'][i], dmags['y'][i]]
            fhout.write(",".join([str(el) for el in line])+"\n")
        fhout.close()


