#!/usr/bin/env python
import subprocess
import pandas as pd
import sys

def process_candidates(csv_filename):
    """
    Lee un archivo CSV con las columnas: Name, RA_deg, DEC_deg y Aperture_arcsec.
    Para cada fila, ejecuta el script mkstamp_RCS.py pasando:
      - RA en grados
      - DEC en grados
      - SIZE en arcmin (Aperture_arcsec / 60)
      - outname (usaremos el campo Name sin espacios)
    """
    # Leer el CSV
    df = pd.read_csv(csv_filename)
    
    # Iterar sobre cada fila (cada candidato)
    for index, row in df.iterrows():
        ra = row["RA_deg"]
        dec = row["DEC_deg"]
        # Convertir la apertura de arcsegundos a arcminutos
        size_arcmin = row["Aperture_arcsec"] / 60.0
        # Usamos el nombre del candidato (quitándole espacios para formar un nombre de archivo válido)
        outname = row["Name"].replace(" ", "")
        
        # Construimos el comando para ejecutar el script
        cmd = f"python mkstamp_RCS.py {ra} {dec} {size_arcmin} {outname}"
        print("Ejecutando:", cmd)
        subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python process_candidates.py <nombre_del_csv>")
        sys.exit(1)
    csv_filename = sys.argv[1]
    process_candidates(csv_filename)
