import numpy as np
from scipy.io.idl import readsav

patch=['0047','0133','0310','0357','1040','1111','1303','1514','1613','1645','2143','2329','2338']

print '# patch chip RA(min) RA(max) DEC(min) DEC(max)'
for npatch in patch:
  file='rcs2phot/'+npatch+'_patchdata/'+npatch
  s=readsav(file+'ra')
  ra=np.array(s.ra)
  s=readsav(file+'dec')
  dec=np.array(s.dec)
  s=readsav(file+'cn')
  cn=np.array(s.cn)

  ucn=np.unique(cn)
  for i in ucn:
    idx=np.where(cn == i)
    print "{0} {1:04d} {2} {3} {4} {5}".format(npatch,i,np.min(ra[idx]),np.max(ra[idx]),np.min(dec[idx]),np.max(dec[idx]))

