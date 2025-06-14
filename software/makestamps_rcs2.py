#!/usr/bin/env python
"""
Descarga y desempaqueta automáticamente los chips Megacam (archivos .fz) del
catálogo RCS‑2 que cubren una coordenada dada.

Uso básico
----------
python rcs2_fetch_stamps.py <RA_deg> <Dec_deg> <SIZE_arcmin> [--exact-only]

- *RA_deg*  y *Dec_deg*  en grados (J2000).
- *SIZE_arcmin* es el tamaño total del campo a cubrir.  El script calcula
  `radius = SIZE/2` para la búsqueda.
- Con `--exact-only` se ignora *SIZE* y se seleccionan solamente los chips cuyo
  bounding‑box incluya la coordenada central.

Ejemplo
~~~~~~~
python rcs2_fetch_stamps.py 224.75 10.3833 2.0 --exact-only --out stamps
"""

import argparse
import logging
import subprocess
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.table import Table

# ───────────────────────────────── CONFIG GLOBAL ──────────────────────────────
DEFAULT_FILTERS = ["g", "r", "i", "z"]         # bandas disponibles en Megacam
CODE_MAP = list("ABCDEFGHIJ")                    # 0→A, …, 8→I, 9→J (en RCS‑2 sólo A‑I)

# Ruta por defecto al mapa de chips (PATCH, CHIP, RAMIN…)
DEFAULT_MAP = Path("/data/data1/RCS2/software/rcs2map_chip.fits")
DEFAULT_IMAGES = Path("/data/data1/RCS2/megacam/Patches/")
DEFAULT_HEADERS = Path("/data/data1/RCS2/HEADERS/")
DEFAULT_OUT = Path("output_fits/")

# ──────────────────────────────── FUNCIONES ──────────────────────────────────

def _decode_chip(chip_int: int) -> tuple[str, str]:
    """Convierte el entero `CHIP` del mapa a (code, ext).

    chip_int = fila_idx*1000 + col_idx*100 + ext
      fila_idx  → 0=A … 8=I
      col_idx   → 0 … 8
      ext       → extensión FITS dentro del multi‑HDU (.fz)

    Devuelve
    -------
    code : str  → 'I4', 'B0', … (para construir el directorio y filename)
    ext  : str  → '00' … '99'  (dos dígitos, para usar con funpack ‑E)
    """
    fila_idx = chip_int // 1000
    col_idx = (chip_int % 1000) // 100
    ext = chip_int % 100

    try:
        letter = CODE_MAP[fila_idx]
    except IndexError:  # índice inesperado
        raise ValueError(f"fila_idx fuera de rango (chip={chip_int})")

    return f"{letter}{col_idx}", f"{ext:02d}"


def find_chips(
    ra_deg: float,
    dec_deg: float,
    radius_arcmin: float,
    map_fits: Path,
    exact_only: bool = False,
):
    """Devuelve lista de tuplas (patch, code, ext) que cubren la región."""

    # Leer tabla del mapa de chips
    with fits.open(map_fits) as hdul:
        data = Table(hdul[1].data)

    # Columnas de la tabla (RAMIN está en horas → convertir a grados)
    ramin = data["RAMIN"] * 15.0
    ramax = data["RAMAX"] * 15.0
    decmin = data["DECMIN"]
    decmax = data["DECMAX"]
    patches = data["PATCH"]
    chips = data["CHIP"]

    # Chips cuyo bounding‑box *contiene* el centro
    center_mask = (
        (ramin <= ra_deg)
        & (ramax >= ra_deg)
        & (decmin <= dec_deg)
        & (decmax >= dec_deg)
    )

    if exact_only:
        mask = center_mask
    else:
        # Caja de búsqueda expandida
        rad_deg = radius_arcmin / 60.0
        dra = rad_deg / np.cos(np.deg2rad(dec_deg))
        ra1, ra2 = ra_deg - dra, ra_deg + dra
        dec1, dec2 = dec_deg - rad_deg, dec_deg + rad_deg

        overlaps = (
            (ra1 < ramax) & (ra2 > ramin) & (dec1 < decmax) & (dec2 > decmin)
        )
        mask = overlaps  # si prefieres exigir *también* center, usa: overlaps & center_mask

    results = []
    for patch, chip_int in zip(patches[mask], chips[mask]):
        code, ext = _decode_chip(int(chip_int))
        results.append((int(patch), code, ext))

    return results


def download_chips(
    chips: list[tuple[int, str, str]],
    out_dir: Path,
    images_root: Path,
    headers_root: Path,
    filters: list[str] = DEFAULT_FILTERS,
):
    """Descarga y desempaqueta cada combinación chip×filtro."""

    out_dir.mkdir(parents=True, exist_ok=True)

    for patch, code, ext in chips:
        pointing = f"{patch:04d}{code}"
        chip_dir = images_root / f"{patch:04d}" / pointing

        for filt in filters:
            extra = "ss" if filt == "z" else ""
            fname_in = chip_dir / f"{extra}{pointing}_{filt}.fz"
            fname_out = out_dir / f"{pointing}_{filt}_{ext}.fits"
            hdr_dir1 = headers_root / f"{patch:04d}" / pointing
            hdr_dir2 = headers_root / f"{patch:04d}"

            hdr_src = (hdr_dir1 / f"{filt}{ext}.hdr"
                    if (hdr_dir1 / f"{filt}{ext}.hdr").exists()
                    else hdr_dir2 / f"{pointing}_{filt}_{ext}.hdr")

            if hdr_src.exists():
                subprocess.run(["cp", str(hdr_src), str(out_dir)], check=True)
                logging.debug(f"Header copiado {hdr_src.name}")
            else:
                logging.warning(f"No existe header {hdr_src}")

            try:
                subprocess.run(
                    ["funpack", "-O", str(fname_out), "-E", ext, str(fname_in)],
                    check=True,
                )
                logging.info(f"Desempaquetado {fname_out}")
            except subprocess.CalledProcessError:
                logging.error(f"funpack falló para {fname_in}")
                continue

            if hdr_src.exists():
                subprocess.run(["cp", str(hdr_src), str(out_dir)], check=True)
                logging.debug(f"Header copiado {hdr_src.name}")
            else:
                logging.warning(f"No existe header {hdr_src}")


# ────────────────────────────────────── CLI ───────────────────────────────────


def main():
    p = argparse.ArgumentParser(description="Descarga stamps Megacam de RCS‑2")
    p.add_argument("ra", type=float, help="RA (grados, J2000)")
    p.add_argument("dec", type=float, help="Dec (grados, J2000)")
    p.add_argument("size", type=float, help="Tamaño del campo (arcmin)")
    p.add_argument("--exact-only", action="store_true", help="Sólo chips que contengan el centro")
    p.add_argument("--map", type=Path, default=DEFAULT_MAP)
    p.add_argument("--images", type=Path, default=DEFAULT_IMAGES)
    p.add_argument("--headers", type=Path, default=DEFAULT_HEADERS)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--log", default="INFO", help="Nivel logging (DEBUG, INFO…)")
    args = p.parse_args()

    logging.basicConfig(level=getattr(logging, args.log.upper()), format="%(levelname)s: %(message)s")

    radius = args.size / 2.0
    chips = find_chips(args.ra, args.dec, radius, args.map, exact_only=args.exact_only)

    if not chips:
        logging.error("No se encontraron chips para esa posición / tamaño")
        return

    logging.info("Chips seleccionados: %s", [f"{p}-{c}" for p, c, _ in chips])
    download_chips(chips, args.out, args.images, args.headers)


if __name__ == "__main__":
    main()
