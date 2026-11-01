#!/usr/bin/env python3
"""Read the DESI DR1 Type 1 AGN catalog with Astropy.

Install: python3 -m pip install astropy
Run:     python3 read_catalog.py
         python3 read_catalog.py /path/to/desidr1_type1cat.fits
         python3 read_catalog.py --targetid 39627884268098267

Without a filename, look beside this script and then in the current directory.
The reader also accepts gzip-compressed FITS files. It does not modify the data.
"""

import argparse
from pathlib import Path

from astropy.io import fits
from astropy.table import Table


def read_catalog(filename):
    """Return the source table, flux scales, and column descriptions.

    TARGETID remains an exact 64-bit integer. Physical column units and
    missing-value masks are retained by Astropy's FITS table reader.
    """
    with fits.open(filename, memmap=False) as hdul:
        catalog = Table.read(hdul, hdu="TYPE1_CATALOG")
        scales = Table.read(hdul, hdu="FLUX_SCALE")
        columns = Table.read(hdul, hdu="COLUMN_INFO")
    if len(catalog) != len(scales) or not (catalog["TARGETID"] == scales["TARGETID"]).all():
        raise ValueError("The catalog and flux-scale TARGETIDs do not match.")
    return catalog, scales, columns


def default_path():
    for directory in (Path(__file__).resolve().parent, Path.cwd()):
        for name in ("desidr1_type1cat.fits", "desidr1_type1cat.fits.gz"):
            path = directory / name
            if path.is_file():
                return path
    return Path(__file__).resolve().parent / "desidr1_type1cat.fits"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("filename", nargs="?", type=Path, help="Path to the FITS catalog")
    parser.add_argument("--targetid", type=int, help="Show one DESI target, using its exact integer ID")
    args = parser.parse_args()
    filename = args.filename if args.filename is not None else default_path()
    if not filename.is_file():
        parser.error(f"File not found: {filename}. Supply the path to your FITS catalog.")
    catalog, scales, columns = read_catalog(filename)
    nls1_both = catalog[catalog["NLS1_FLAG_BOTH"] == 1]

    print(f"File: {filename}")
    print(f"Catalog: {len(catalog):,} sources, {len(catalog.colnames)} columns")
    print(f"Flux scales: {len(scales):,} sources")
    print(f"Column descriptions: {len(columns)}")
    print(f"NLS1s in both profiles: {len(nls1_both):,}")

    selected = (catalog[catalog["TARGETID"] == args.targetid]
                if args.targetid is not None else catalog[:5])
    if args.targetid is not None and len(selected) == 0:
        parser.error(f"TARGETID {args.targetid} is not in this catalog.")
    display = ["TARGETID", "Z", "NLS1_FLAG_fitl", "NLS1_FLAG_fitg",
               "L5100", "FWHM_Broad_Hbeta_fitl", "FWHM_Broad_Hbeta_fitg"]
    print("\nSelected target:" if args.targetid is not None else "\nFirst five sources:")
    selected[display].pprint(max_width=-1)

    # Examples for your own analysis:
    # target = catalog[catalog["TARGETID"] == 39627884268098267]
    # print(columns[columns["COLUMN"] == "MBH_fitg"])
    # line_flux = catalog["Flux_OIII5007_fitl"] * scales["UNIT_fitl"] * 1e-17
    # line_flux is the integrated [O III] flux in erg s^-1 cm^-2.


if __name__ == "__main__":
    main()
