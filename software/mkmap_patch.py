import numpy as np
from scipy.io.idl import readsav

patch=['0047','0133','0310','0357','1040','1111','1303','1514','1613','1645','2143','2329','2338']

print '# patch RA(min) RA(max) DEC(min) DEC(max)'
for npatch in patch:
  file='rcs2phot/'+npatch+'_patchdata/'+npatch
  s=readsav(file+'ra')
  minra=min(np.array(s.ra))
  maxra=max(np.array(s.ra))
  s=readsav(file+'dec')
  mindec=min(np.array(s.dec))
  maxdec=max(np.array(s.dec))
  print npatch,minra,maxra,mindec,maxdec

#ucn=np.unique(cn)

#for i in ucn:
#  idx=np.where(cn == i)
#  print np.min(ra[idx]),np.max(ra[idx]),np.min(dec[idx]),np.max(dec[idx])
#  plt.plot(ra[idx],dec[idx],'ro',ms=1)
#  plt.show()

