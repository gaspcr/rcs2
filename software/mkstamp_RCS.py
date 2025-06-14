#!/usr/bin/env python
import sys
import os
import numpy as np
from astropy.io import fits, ascii
from astropy.table import Table
def findimages(ra, dec, radius):
    """
    Busca los chips que contienen la región definida por (ra, dec) y un radio (en arcmin).
    Se espera que 'radius' venga en arcminutos, y se convierte a grados para los cálculos.
    """
    # Lista para convertir parte del número de chip a letra
    icode = ['A','B','C','D','E','F','G','H','I','J']
    
    # Convertir el radio de arcmin a grados (1 arcmin = 1/60 grados)
    radius_deg = radius / 60.0
    radeg = 180.0 / np.pi

    # Cargar la tabla con la información de los chips
    datafits = fits.getdata('/data/data1/RCS2/software/rcs2map_chip.fits')
    data = Table(datafits)

    # Definir los límites en DEC y RA (ya en grados)
    dec1 = dec - radius_deg
    dec2 = dec + radius_deg
    ra1 = ra - radius_deg / np.cos(max([abs(dec1), abs(dec2)])/radeg)
    ra2 = ra + radius_deg / np.cos(max([abs(dec1), abs(dec2)])/radeg)

    # Extraer límites de los chips; para RA se convierte de "horas" a grados (1h = 15°)
    ramin = 15 * np.array(data['RAMIN'])
    ramax = 15 * np.array(data['RAMAX'])
    decmin = np.array(data['DECMIN'])
    decmax = np.array(data['DECMAX'])
    patch = np.array(data['PATCH'])
    chip = np.array(data['CHIP'])
    # Seleccionar aquellos chips que solapan con la caja definida
    ix = np.where((ra1 < ramax) & (ra2 > ramin) & (dec1 < decmax) & (dec2 >= decmin))[0]
    # Abrir el archivo 'outlist' para escribir los identificadores
    with open('outlist', 'a') as f:
        for i in ix:
            nchip = chip[i]
            # Descomponer el número de chip en partes:
            nchip1 = int(np.fix(nchip / 1000))
            nchip2 = int(np.fix((nchip - nchip1 * 1000) / 100))
            nchip3 = int(np.fix(nchip - nchip1 * 1000 - nchip2 * 100))
            line = "{:04d}{}{} {}\n".format(patch[i], icode[nchip1], nchip2, nchip3)
            f.write(line)
            print(line.strip())
def getimages():
    """
    Lee el archivo 'outlist' y, para cada entrada, construye y ejecuta los comandos para:
      - Descomprimir la imagen (.fz) usando 'funpack' generando un archivo FITS.
      - Copiar la cabecera (.hdr) a la carpeta actual.
    """
    # Rutas base para las imágenes y encabezados (ajustar según corresponda)
    path_images = "/data/data1/RCS2/megacam/Patches"
    path_headers = "/data/data1/RCS2/HEADERS"
    images = ascii.read("outlist")

    filters = ['g','r','i','z']
    for row in images:
        pointing = row[0]
        patch_val = pointing[0:4]
        extension = row[1]  # Se asume que la segunda columna es 'extension'
        
        for filter in filters:
            extra = "ss" if filter == "z" else ""
            im_in = "{}/{}/{}/{}{}_{}.fz".format(path_images, patch_val, pointing, extra, pointing, filter)
            im_out = "{}_{}_{}.fits".format(pointing, filter, extension)
            hdr = "{}/{}/{}_{}_{}.hdr".format(path_headers, patch_val, pointing, filter, extension)
            cmd = "funpack -O {} -E {} {}".format(im_out, extension, im_in)
            print(cmd)
            os.system(cmd)
            cmd = "cp {} .".format(hdr)
            print(cmd)
            os.system(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Syntax: {} RA(deg) DEC(deg) SIZE(arcmin) outname".format(sys.argv[0]))
        sys.exit(1)
        
    ra = float(sys.argv[1])
    dec = float(sys.argv[2])
    size = float(sys.argv[3])
    name = sys.argv[4]
    
    # Opcional: cálculo de sizepix y scale si son necesarios para otro propósito
    scale = 0.2
    sizepix = int(size/scale*60)
    
    print("Parámetros:", ra, dec, size, name)
    # Se toma el radio como la mitad del tamaño (en arcmin)
    findimages(ra, dec, size/2.0)
    getimages()
    print("Proceso completado.")