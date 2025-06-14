def getimages():

  import sys,re,os
  from astropy.io import ascii

  path_images="/data1/RCS2/megacam/Patches/"
  path_headers="/data1/RCS2/HEADERS/"
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
      os.system(cmd)

