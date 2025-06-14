def findimages(ra,dec,radius):
  from astropy.io import fits 
  from astropy.table import Table
  import numpy as np

  icode=['A','B','C','D','E','F','G','H','I','J']

#ra=51.8625
#dec=-13.4397
#radius=2 # in arcmin
  radius=radius/60.
  radeg=180./3.141592

  datafits=fits.getdata('/data1/RCS2/software/rcs2map_chip.fits')
  data=Table(datafits)

  dec1=dec-radius/60.
  dec2=dec+radius/60.
  ra1=ra-radius/np.cos(max([abs(dec1),abs(dec2)])/radeg)
  ra2=ra+radius/np.cos(max([abs(dec1),abs(dec2)])/radeg)
#print(ra1,ra2,dec1,dec2)

  ramin=15*np.array(data['RAMIN'])
  ramax=15*np.array(data['RAMAX'])
  decmin=np.array(data['DECMIN'])
  decmax=np.array(data['DECMAX'])
  patch=np.array(data['PATCH'])
  chip=np.array(data['CHIP'])

  ix=np.where((ra1 < ramax) & (ra2 > ramin) & (dec1 < decmax) & (dec2 >= decmin))

  f=open('outlist','a')

  for i in range(len(ix[0])): 
    nchip=chip[ix][i]
    nchip1=np.int_(np.fix(nchip/1000))
    nchip2=np.int_(np.fix((nchip-nchip1*1000)/100))
    nchip3=np.int_(np.fix(nchip-nchip1*1000-nchip2*100))
    f.write("{:04d}{}{} {}\n".format(patch[ix][i],icode[nchip1],nchip2,nchip3))
    print("{:04d}{}{} {}".format(patch[ix][i],icode[nchip1],nchip2,nchip3))

  f.close()

