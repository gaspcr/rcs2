
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

  datafits=fits.getdata('/data/data1/RCS2/software/rcs2map_chip.fits')
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


def getimages():

  import sys,re,os
  from astropy.io import ascii

  path_images="data/data1/RCS2/megacam/Patches/"
  path_headers="data/data1/RCS2/HEADERS/"
  images=ascii.read("outlist")

  filters=['g','r','i','z']
  for i in range(len(images)):
    patch=images[i][0][0:4]
    pointing=images[i][0]
    extension=images[i][1]

    for filter in filters:
      if filter == "z":
        extra="ss"
      else:
        extra=""
      im_in="{}{}/{}/{}{}_{}.fz".format(path_images,patch,pointing,extra,pointing,filter)
      im_out="{}_{}_{}.fits".format(pointing,filter,extension)
      hdr="{}{}/{}_{}_{}.hdr".format(path_headers,patch,pointing,filter,extension)
      cmd="funpack -O {} -E {} {}".format(im_out,extension,im_in)
      print(cmd)
      os.system(cmd)
      cmd="cp {} .".format(hdr)
      print(cmd)
#      os.system(cmd)

#!/usr/bin/env python 
import sys,re,os 

#os.environ['LD_LIBRARY_PATH'] =  '/usr/local/lib'

if len(sys.argv) < 4:
        print("Syntax: "+ sys.argv[0] + " RA(deg) DEC(deg) SIZE(arcmin) outname")
        sys.exit() 
ra = float(sys.argv[1]) 
dec = float(sys.argv[2])
size = float(sys.argv[3])
name = sys.argv[4]
scale= 0.2
sizepix=int(size/scale*60)

radius=size/2.
print(ra,dec,size,name)
findimages(ra,dec,radius)

getimages()

