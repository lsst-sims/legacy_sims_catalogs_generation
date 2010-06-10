import sys
import movingObjectCatalogs as moc
import uIBackEnd as ui
import numpy as n


## SET UP FOR DIASOURCES

# get obshistid for this pointing from command line, as well as output file name
obshistid = sys.argv[1]
prefix = ''
prefix = sys.argv[2]
trimcat_output = prefix+'diasource_' + '%s' %(sys.argv[1])

#    	OPSIM
# query opsim - imageSimDB.py query (for OPSIM ONLY)
# ophistid = 85471141 
opsimParams = ui.queryOnObsHistID(obshistid)

print "Working on obshistid: %s, writing to files based %s" %(obshistid, trimcat_output)

radius_fov = 1.8   # radius of the field of view
dtExp = 17.0  # delta time exposure one to another


## 	MOVING OBJECTS
## query movingobject tables for moving objects
rootSEDdir = 'dat' # rootsed dir = directory where SEDS and thruputs live
outList0, outList1, descriptionList = moc.buildMovingObjectCatalog(opsimParams['fieldradeg'], 
                                                                   opsimParams['fielddecdeg'], 
                                                                   radius_fov,
                                                                   opsimParams['expmjd'], opsimParams['filter'],
                                                                   opsimParams['m5sigma_ps'], SNRcutoff=5, 
                                                                   verbose=True,  # put this to False later
                                                                   dtExp = dtExp,
                                                                   startup_pyoorb=True,
                                                                   rootSEDdir=rootSEDdir)
## write moving objects to diasource catalogs
#for i in range(len(outList1)):
#    print outList1[i]

filterdict = {'u':0, 'g':1, 'r':2, 'i':3, 'z':4, 'y':5}
filternum = filterdict[opsimParams['filter']]
expmjd= opsimParams['expmjd']
ampexposureid = obshistid

# open output file
fileout = open(trimcat_output+"_0", 'w')

# descriptionList = ['objid', 'ra', 'decl', 'raError', 'declError', 'magFilter', 'magError']
diasourceid = 0
for obj in outList0:
    ssmid = obj[0]
    objid = ssmid
    ra = obj[1]
    dec = obj[2]
    ast_err = obj[3]
    magout = obj[5]
    magerr = obj[6]
    flux_ratio = n.power(10, 0.4*(opsimParams['m5sigma_ps']-magout))
    snr = 5 * (flux_ratio)
    print >>fileout, diasourceid, ampexposureid, "NULL", filternum, 'NULL', objid, '2', '2', ssmid, ra, ast_err, ast_err, dec, ast_err, ast_err, magout, magerr, magout, magerr, magout, magerr, magout, magerr, "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", ra, ast_err, dec, ast_err, expmjd, "15.0", "0.0", magout, magerr, magout, magerr, magout, magerr, magout, magerr, magout, magerr, magout, magerr, "NULL", "0.0", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", snr, "0.8", "100.0", "100.0", "200.0", "200.0", "1.0", "807", "Y", "N", "NULL", "NULL", "NULL", "NULL"
    # increment diasource id (unique across objects)
    diasourceid = diasourceid + 1
fileout.close()


# open output file
fileout = open(trimcat_output+"_1", 'w')
# descriptionList = ['objid', 'ra', 'decl', 'raError', 'declError', 'magFilter', 'magError']
diasourceid = 0
for obj in outList1:
    ssmid = obj[0]
    objid = ssmid
    ra = obj[1]
    dec = obj[2]
    ast_err = obj[3]
    magout = obj[5]
    magerr = obj[6]
    flux_ratio = n.power(10, 0.4*(opsimParams['m5sigma_ps']-magout))
    snr = 5 * (flux_ratio)
    print >>fileout, diasourceid, ampexposureid, "NULL", filternum, 'NULL', objid, '2', '2', ssmid, ra, ast_err, ast_err, dec, ast_err, ast_err, magout, magerr, magout, magerr, magout, magerr, magout, magerr, "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", ra, ast_err, dec, ast_err, expmjd, "15.0", "0.0", magout, magerr, magout, magerr, magout, magerr, magout, magerr, magout, magerr, magout, magerr, "NULL", "0.0", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", snr, "0.8", "100.0", "100.0", "200.0", "200.0", "1.0", "807", "Y", "N", "NULL", "NULL", "NULL", "NULL"
    # increment diasource id (unique across objects)
    diasourceid = diasourceid + 1
fileout.close()




# output for Francesco's diasource schema
#diasource(unique,bigint, notnull=counter), ampexposureid(bigint,notnull=obshistidid), diasourceTold(bigint,NULL), 
# filterID(tinyint,notnull=0-6), objid(bigint,null), movingobjectid(bigint,==objid), prochistidID(int, notnull),
# scId(int,notnull), ssmID(bigint,null=movingobjectid), ra(double,notnull), raerrfordetection(notnull), 
# raerrforwcs(float,null), decl(double,notnull), declerrofordetection (float,notnull), declerrforwcs(float, null)
# xflux(null), xfluxerr( null), yflux (null), yfluxerr(null), raflux (null), rafluxerr(null), declflux (null),
# declfluxerr (null), xpeak(null), ypeak (null), rapeak(null), declpeak(null), xAstrom(null), xAstromErr(null),
# yAstrom(null), yAstromErr (null), raAstrom(null), raAstromErr(null), declAstrom(null), ddeclAstromErr(null),
# taimidpoint(double not null), tairange(not null), lengthDeg(not null), psfFlux(not null), psfFluxErr(notnull), 
# apFlux(notnull), apFluxErr(notnull), modelFlux(notnull), modelFluxErr(null), instFlux(not null), instFluxErr(notnull),
# nonGrayCorrFlux(null, nonGrayCorrFluxErr(null), atmCorrFlux(null), atmCorrFluxErr(null), apDia(null), refMag(null),
# Ixx(null), IxxErr(null), Iyy(null), IyyErr(null), ixy(null), IxyErr(null), SNR(snr), chi2(notnull), 
# valx1 (double, notnull), valx2 (doublenotnull), valy1(double, notnull), valy2(double, notnull), valxy(double, notnull)
# obscod(null = '807' char), isSynthetic ('y'), mopsStatus(NULL), flagForAssociation(null), flagForDetection(null)
# flagforWCs(NULL), flagClassification(NULL)


# output for DC3a diasource schema
# diasourceid(uniquebigint), ampexposureid(bigint, notnull), diasourceTold(bigint,NULL), filterid(tinyint, notnull)
# objid(bigint, NULL), movingobjectid(bigint, ==objid), xAstrom(double, notnull), xAstromErr (double)
# yAstrom(double,notnull), yAstromErr(double), ra(double, notnull), raErrForDetection(double), raErrForWCS(double),
# decl(double, notnull), declErrForDetection(double), declErrForWCS(double), 
# taiMidPoint(double,notnull), taiRange(double,notNull),  
# ixx(null), ixxerr(null), iyy(null), iyyerr(null), ixy(null), ixyerr(null), psfFlux(double, notNull), psfFluxErr(Null?)
# apFlux(double, notnull), apFluxErr(null), modelFlux(double,notnull), modelfluxerr(null?), instflux(double,notnull),
# instfluxerr(null?), apDia(float, null), flagForClassification(bigint, null), flagForDetection(bigint, null),
# snr (float, not null), chi2(float, notnull)
