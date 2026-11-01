# DESI DR1 Type 1 AGN catalogue (Yao et al. 2026)

This catalogue contains **114,754 Type 1 AGNs**, one row per DESI
TARGETID, and **167 columns** expanded from the paper's Table 2.
The release preserves the measurements used by the paper. No spectra were
refitted, and no additional signal-to-noise or parameter-quality cuts were applied.

## Files and reading

- `desi_dr1_type1_catalog.fits`: uncompressed FITS (149.4 MiB).
- `desi_dr1_type1_catalog.fits.gz`: losslessly compressed copy (66.6 MiB), convenient for GitHub distribution.
- `SHA256SUMS.txt`: checksums for both FITS files and this README.
- `validation.json`: coverage, round-trip, and numerical consistency checks.

The compressed and uncompressed files contain identical FITS bytes. Only one
copy needs to be distributed. Astropy reads either directly:

```python
from astropy.table import Table
catalog = Table.read("desi_dr1_type1_catalog.fits.gz", hdu="TYPE1_CATALOG")
scales = Table.read("desi_dr1_type1_catalog.fits.gz", hdu="FLUX_SCALE")
nls1_both = catalog[catalog["NLS1_FLAG_BOTH"] == 1]
```

| Extension | Content |
|---|---|
| PRIMARY | Release conventions and version information. |
| TYPE1_CATALOG | Table 2, with 167 columns in the displayed table order. |
| FLUX_SCALE | TARGETID, UNIT_fitl, UNIT_Halpha_fitl, UNIT_fitg, UNIT_Halpha_fitg, UNIT_DEFAULT_fitl. |
| COLUMN_INFO | Exact expanded column names, units, FITS formats, descriptions, source mappings, Table 2 row numbers, and missing counts. |
| PROVENANCE | Input file names, roles, row counts, and SHA-256 hashes. |

Both per-source extensions have identical TARGETID order, sorted numerically.
TARGETID is a signed 64-bit integer (FITS `K`), never a floating-point number.
Measurements are 64-bit floats (`D`), without rounding. Missing measurements
are IEEE NaN. Real zeros, including zero errors, are preserved.

## Profiles and classification

`fitl` denotes Lorentzian fits. `fitg` denotes **two Gaussian components**,
mapped from the internal `fitdg` products. The old single-Gaussian `fitg`
input files are not used. `BROAD_PROFILE` stores `lorentzian` or `dgaussian`.
For the double-Gaussian fits, the unsuffixed broad-line flux is G1+G2 and
the broad-line FWHM describes the summed profile, not either component.

For each profile, `NLS1_FLAG=1` requires both

```
FWHM_Broad_Hbeta - FWHM_Broad_Hbeta_Err < 2000 km/s
FWHM_Broad_Hbeta < 2200 km/s
```

Widths must be finite and positive, and errors finite and nonnegative.
Flag `0` means the criterion is not met; `-1` means the inputs are invalid.
`NLS1_FLAG_BOTH=1` requires both profile flags to be 1, `-1` means either
profile is unclassifiable, and 0 covers the remaining cases. These flags
follow the criterion in the paper's current plotting code, not the older
NLS1/BOUNDARY/BLS1 labels in the internal sample table.

| Selection | Count |
|---|---:|
| All Type 1 AGNs | 114,754 |
| NLS1, Lorentzian | 25,628 |
| NLS1, two Gaussians | 13,359 |
| NLS1 in both | 11,012 |
| Invalid two-Gaussian classification inputs | 3 |
| Halpha/BPT input coverage (z < 0.35) | 15,390 |

Halpha/BPT measurements are NaN outside the 15,390-source z<0.35 input subset.
Within that subset, individual derived ratios may also be unavailable.
The BPT ratios are linear, and the [S II] numerator is the sum of 6716 and 6731.
The non-BPT [O III]/narrow-Hbeta columns retain the source parameter-table
convention (a finite zero numerator is allowed); the BPT products require
positive numerator and denominator and Halpha subset membership.

## Flux scales and units

All `Flux_*` values and their uncertainties preserve the fitted units in
Table 2. A separate scale is supplied for each target and fitting region:

```
integrated line flux [erg s^-1 cm^-2] = Flux_line * UNIT * 1e-17
continuum f_lambda [erg s^-1 cm^-2 Angstrom^-1] = Flux_5100A * UNIT * 1e-17
```

Use `UNIT_fitl` / `UNIT_fitg` for the Hbeta-region columns, and
`UNIT_Halpha_fitl` / `UNIT_Halpha_fitg` for Halpha-region columns, including
the Halpha G1/G2 fluxes. Apply the same factor to flux uncertainties.
The Angstrom^-1 factor applies to continuum density, not integrated line flux.
Because the scale varies by source, flux columns have no fixed physical
`TUNIT`; their units and conversion are documented here and in COLUMN_INFO.
Luminosity, mass, FWHM and EW columns have physical FITS `TUNIT` values.

The original Lorentzian parameter pipeline interprets absent `UNIT` as 1.
This release preserves that convention for 112,853 rows,
identified by `FLUX_SCALE.UNIT_DEFAULT_fitl=1`. These factors reproduce the
stored line luminosities; this export does not independently recalibrate fluxes.

`L5100` and its errors come from the host-subtracted continuum product.
`D4000` and `Dn4000` are the original spectrum/product indices, not the
separately measured host-only indices. EWs are in rest-frame Angstrom.

## Black-hole mass and accretion rate

`MBH_<prof>` and `mdot_<prof>` are the existing `MBH_DW19` and `mdot_DW19`
columns, in linear units. Both profiles use the common host-subtracted
`L5100` and their own RFe:

```
log10(R_Hbeta / light-day) = 1.65 + 0.45*log10(L5100/1e44) - 0.35*RFe
MBH = 0.75 * R_Hbeta * FWHM^2 / G          (converted to solar masses)
mdot = 20.1 * ((L5100/1e44)/0.75)^1.5 * (MBH/1e7)^(-2)
```

`mdot` is a dimensionless mass-accretion-rate proxy, not Lbol/Ledd.

**Existing width/mass inconsistency:** the source two-Gaussian Hbeta FWHM
was evaluated on a 501-point velocity grid. The source mass pipeline
re-evaluated the summed profile on a 1,201-point grid before calculating
MBH and mdot. This export preserves both existing products. Consequently,
substituting the released `FWHM_Broad_Hbeta_fitg` into the above mass formula
does not always reproduce the released `MBH_fitg`. Among the
114,707 finite comparisons,
the median absolute difference is
0.003526 dex,
1,157 exceed 0.1 dex,
and the maximum is 3.9601 dex.
The exported width and mass are not a numerically consistent pair for these
objects. This is an unresolved property of the paper inputs, not a FITS
conversion error. Zero errors and parameters at fitting bounds are also
preserved and should not be interpreted as exact measurements.

## Reproduction and verification

From the project root, run:

```bash
python3 collectpars/build_type1_catalog.py --data-dir collectpars --output-dir catalog_release
```

Dependencies: Python 3, NumPy, pandas, and Astropy. Input CSV files are
identified by hashes in PROVENANCE; rebuilding requires those files.
The builder checks unique exact integer identifiers, complete joins,
profile identity, Halpha coverage, every exported cell on FITS read-back,
FITS checksums, Gaussian flux sums, RFe, [O III] luminosities, BPT ratios,
and byte-identical gzip decompression. See `validation.json` for results.

## Expanded Table 2 columns

For each table row, placeholders are expanded in the order shown in the
paper, with `fitl` before `fitg`. `COLUMN_INFO` contains the source mappings.
`--` below denotes a dimensionless quantity or identifier.

| No. | Column | Unit | Description |
|---:|---|---|---|
| 1 | `TARGETID` | -- | DESI target identifier. |
| 2 | `NLS1_FLAG_fitl` | -- | 1: FWHM-error < 2000 and FWHM < 2200 km/s; 0: fails; -1: invalid width/error. |
| 3 | `NLS1_FLAG_fitg` | -- | 1: FWHM-error < 2000 and FWHM < 2200 km/s; 0: fails; -1: invalid width/error. |
| 4 | `NLS1_FLAG_BOTH` | -- | 1: NLS1 in both profiles; 0: not both; -1: either profile is unclassifiable. |
| 5 | `Z` | -- | DESI redshift used in this work. |
| 6 | `snr5100` | -- | Median continuum signal-to-noise ratio near rest-frame 5100 Angstrom. |
| 7 | `D4000` | -- | D4000 index from the original spectrum/product (not the host-only index). |
| 8 | `Dn4000` | -- | Narrow Dn(4000) index from the original spectrum/product. |
| 9 | `L5100` | erg s-1 | Host-subtracted monochromatic luminosity lambda L_lambda at 5100 Angstrom. |
| 10 | `L5100_err` | erg s-1 | Uncertainty on L5100. |
| 11 | `relerr_L5100` | -- | Relative uncertainty on L5100, as stored in the source product. |
| 12 | `BROAD_PROFILE_fitl` | -- | Broad-Hbeta profile model: lorentzian or dgaussian. |
| 13 | `BROAD_PROFILE_fitg` | -- | Broad-Hbeta profile model: lorentzian or dgaussian. |
| 14 | `CHI2_RED_fitl` | -- | Reduced chi-square of the Hbeta-region fit. |
| 15 | `CHI2_RED_fitg` | -- | Reduced chi-square of the Hbeta-region fit. |
| 16 | `Flux_5100A_fitl` | fit flux unit | Power-law continuum flux density at rest-frame 5100 Angstrom. |
| 17 | `Flux_5100A_fitg` | fit flux unit | Power-law continuum flux density at rest-frame 5100 Angstrom. |
| 18 | `Flux_5100A_Err_fitl` | fit flux unit | Uncertainty on Flux_5100A. |
| 19 | `Flux_5100A_Err_fitg` | fit flux unit | Uncertainty on Flux_5100A. |
| 20 | `PL_Index_5100A_fitl` | -- | Power-law continuum index. |
| 21 | `PL_Index_5100A_fitg` | -- | Power-law continuum index. |
| 22 | `PL_Index_5100A_Err_fitl` | -- | Uncertainty on PL_Index_5100A. |
| 23 | `PL_Index_5100A_Err_fitg` | -- | Uncertainty on PL_Index_5100A. |
| 24 | `Flux_FeII_fitl` | fit flux unit | Hbeta-region FeII Flux. |
| 25 | `Flux_FeII_fitg` | fit flux unit | Hbeta-region FeII Flux. |
| 26 | `Flux_Broad_Hbeta_fitl` | fit flux unit | Hbeta-region Broad_Hbeta Flux. |
| 27 | `Flux_Broad_Hbeta_fitg` | fit flux unit | Hbeta-region Broad_Hbeta Flux. Total summed broad profile. |
| 28 | `Flux_Narrow_Hbeta_fitl` | fit flux unit | Hbeta-region Narrow_Hbeta Flux. |
| 29 | `Flux_Narrow_Hbeta_fitg` | fit flux unit | Hbeta-region Narrow_Hbeta Flux. |
| 30 | `Flux_OIII4959_fitl` | fit flux unit | Hbeta-region OIII4959 Flux. |
| 31 | `Flux_OIII4959_fitg` | fit flux unit | Hbeta-region OIII4959 Flux. |
| 32 | `Flux_OIII5007_fitl` | fit flux unit | Hbeta-region OIII5007 Flux. |
| 33 | `Flux_OIII5007_fitg` | fit flux unit | Hbeta-region OIII5007 Flux. |
| 34 | `Flux_FeII_Err_fitl` | fit flux unit | Uncertainty on Hbeta-region FeII Flux. |
| 35 | `Flux_FeII_Err_fitg` | fit flux unit | Uncertainty on Hbeta-region FeII Flux. |
| 36 | `Flux_Broad_Hbeta_Err_fitl` | fit flux unit | Uncertainty on Hbeta-region Broad_Hbeta Flux. |
| 37 | `Flux_Broad_Hbeta_Err_fitg` | fit flux unit | Uncertainty on Hbeta-region Broad_Hbeta Flux. Total summed broad profile. |
| 38 | `Flux_Narrow_Hbeta_Err_fitl` | fit flux unit | Uncertainty on Hbeta-region Narrow_Hbeta Flux. |
| 39 | `Flux_Narrow_Hbeta_Err_fitg` | fit flux unit | Uncertainty on Hbeta-region Narrow_Hbeta Flux. |
| 40 | `Flux_OIII4959_Err_fitl` | fit flux unit | Uncertainty on Hbeta-region OIII4959 Flux. |
| 41 | `Flux_OIII4959_Err_fitg` | fit flux unit | Uncertainty on Hbeta-region OIII4959 Flux. |
| 42 | `Flux_OIII5007_Err_fitl` | fit flux unit | Uncertainty on Hbeta-region OIII5007 Flux. |
| 43 | `Flux_OIII5007_Err_fitg` | fit flux unit | Uncertainty on Hbeta-region OIII5007 Flux. |
| 44 | `FWHM_FeII_fitl` | km s-1 | Hbeta-region FeII FWHM. |
| 45 | `FWHM_FeII_fitg` | km s-1 | Hbeta-region FeII FWHM. |
| 46 | `FWHM_Broad_Hbeta_fitl` | km s-1 | Hbeta-region Broad_Hbeta FWHM. |
| 47 | `FWHM_Broad_Hbeta_fitg` | km s-1 | Hbeta-region Broad_Hbeta FWHM. Total summed broad profile. Source width uses a 501-point grid; see README. |
| 48 | `FWHM_Narrow_Hbeta_fitl` | km s-1 | Hbeta-region Narrow_Hbeta FWHM. |
| 49 | `FWHM_Narrow_Hbeta_fitg` | km s-1 | Hbeta-region Narrow_Hbeta FWHM. |
| 50 | `FWHM_OIII4959_fitl` | km s-1 | Hbeta-region OIII4959 FWHM. |
| 51 | `FWHM_OIII4959_fitg` | km s-1 | Hbeta-region OIII4959 FWHM. |
| 52 | `FWHM_OIII5007_fitl` | km s-1 | Hbeta-region OIII5007 FWHM. |
| 53 | `FWHM_OIII5007_fitg` | km s-1 | Hbeta-region OIII5007 FWHM. |
| 54 | `FWHM_FeII_Err_fitl` | km s-1 | Uncertainty on Hbeta-region FeII FWHM. |
| 55 | `FWHM_FeII_Err_fitg` | km s-1 | Uncertainty on Hbeta-region FeII FWHM. |
| 56 | `FWHM_Broad_Hbeta_Err_fitl` | km s-1 | Uncertainty on Hbeta-region Broad_Hbeta FWHM. |
| 57 | `FWHM_Broad_Hbeta_Err_fitg` | km s-1 | Uncertainty on Hbeta-region Broad_Hbeta FWHM. Total summed broad profile. Source width uses a 501-point grid; see README. |
| 58 | `FWHM_Narrow_Hbeta_Err_fitl` | km s-1 | Uncertainty on Hbeta-region Narrow_Hbeta FWHM. |
| 59 | `FWHM_Narrow_Hbeta_Err_fitg` | km s-1 | Uncertainty on Hbeta-region Narrow_Hbeta FWHM. |
| 60 | `FWHM_OIII4959_Err_fitl` | km s-1 | Uncertainty on Hbeta-region OIII4959 FWHM. |
| 61 | `FWHM_OIII4959_Err_fitg` | km s-1 | Uncertainty on Hbeta-region OIII4959 FWHM. |
| 62 | `FWHM_OIII5007_Err_fitl` | km s-1 | Uncertainty on Hbeta-region OIII5007 FWHM. |
| 63 | `FWHM_OIII5007_Err_fitg` | km s-1 | Uncertainty on Hbeta-region OIII5007 FWHM. |
| 64 | `Flux_Broad_Hbeta_G1_fitg` | fit flux unit | Flux_Broad_Hbeta_G1 of the double-Gaussian Hbeta model. |
| 65 | `Flux_Broad_Hbeta_G2_fitg` | fit flux unit | Flux_Broad_Hbeta_G2 of the double-Gaussian Hbeta model. |
| 66 | `FWHM_Broad_Hbeta_G1_fitg` | km s-1 | FWHM_Broad_Hbeta_G1 of the double-Gaussian Hbeta model. |
| 67 | `FWHM_Broad_Hbeta_G2_fitg` | km s-1 | FWHM_Broad_Hbeta_G2 of the double-Gaussian Hbeta model. |
| 68 | `Broad_Hbeta_G1_Fraction_fitg` | -- | Broad_Hbeta_G1_Fraction of the double-Gaussian Hbeta model. |
| 69 | `L_OIII5007_fitl` | erg s-1 | [O III] 5007 luminosity. |
| 70 | `L_OIII5007_fitg` | erg s-1 | [O III] 5007 luminosity. |
| 71 | `EW_Broad_Hbeta_fitl` | Angstrom | Rest-frame broad-Hbeta equivalent width. |
| 72 | `EW_Broad_Hbeta_fitg` | Angstrom | Rest-frame broad-Hbeta equivalent width. |
| 73 | `EW_OIII5007_fitl` | Angstrom | Rest-frame [O III] 5007 equivalent width. |
| 74 | `EW_OIII5007_fitg` | Angstrom | Rest-frame [O III] 5007 equivalent width. |
| 75 | `EW_OIII5007_Err_fitl` | Angstrom | Uncertainty on EW_OIII5007. |
| 76 | `EW_OIII5007_Err_fitg` | Angstrom | Uncertainty on EW_OIII5007. |
| 77 | `RFe_fitl` | -- | Fe II (4434-4684 Angstrom) to total broad-Hbeta flux ratio. |
| 78 | `RFe_fitg` | -- | Fe II (4434-4684 Angstrom) to total broad-Hbeta flux ratio. |
| 79 | `RFe_Err_fitl` | -- | Uncertainty on RFe. |
| 80 | `RFe_Err_fitg` | -- | Uncertainty on RFe. |
| 81 | `OIII5007_to_Narrow_Hbeta_fitl` | -- | [O III] 5007 to narrow-Hbeta flux ratio. |
| 82 | `OIII5007_to_Narrow_Hbeta_fitg` | -- | [O III] 5007 to narrow-Hbeta flux ratio. |
| 83 | `MBH_fitl` | solMass | Single-epoch black-hole mass using the RFe-dependent DW19 relation. See README for fitg width convention. |
| 84 | `MBH_fitg` | solMass | Single-epoch black-hole mass using the RFe-dependent DW19 relation. See README for fitg width convention. |
| 85 | `mdot_fitl` | -- | Dimensionless mass-accretion-rate proxy using the DW19 mass. |
| 86 | `mdot_fitg` | -- | Dimensionless mass-accretion-rate proxy using the DW19 mass. |
| 87 | `CHI2_RED_Halpha_fitl` | -- | Reduced chi-square of the Halpha-region fit. |
| 88 | `CHI2_RED_Halpha_fitg` | -- | Reduced chi-square of the Halpha-region fit. |
| 89 | `Flux_5100A_Halpha_fitl` | fit flux unit | Continuum flux density at 5100 Angstrom from the Halpha-region fit. |
| 90 | `Flux_5100A_Halpha_fitg` | fit flux unit | Continuum flux density at 5100 Angstrom from the Halpha-region fit. |
| 91 | `Flux_Broad_Halpha_Halpha_fitl` | fit flux unit | Halpha-region Broad_Halpha Flux. |
| 92 | `Flux_Broad_Halpha_Halpha_fitg` | fit flux unit | Halpha-region Broad_Halpha Flux. Total summed broad profile. |
| 93 | `Flux_Narrow_Halpha_Halpha_fitl` | fit flux unit | Halpha-region Narrow_Halpha Flux. |
| 94 | `Flux_Narrow_Halpha_Halpha_fitg` | fit flux unit | Halpha-region Narrow_Halpha Flux. |
| 95 | `Flux_NII6548_Halpha_fitl` | fit flux unit | Halpha-region NII6548 Flux. |
| 96 | `Flux_NII6548_Halpha_fitg` | fit flux unit | Halpha-region NII6548 Flux. |
| 97 | `Flux_NII6583_Halpha_fitl` | fit flux unit | Halpha-region NII6583 Flux. |
| 98 | `Flux_NII6583_Halpha_fitg` | fit flux unit | Halpha-region NII6583 Flux. |
| 99 | `Flux_SII6716_Halpha_fitl` | fit flux unit | Halpha-region SII6716 Flux. |
| 100 | `Flux_SII6716_Halpha_fitg` | fit flux unit | Halpha-region SII6716 Flux. |
| 101 | `Flux_SII6731_Halpha_fitl` | fit flux unit | Halpha-region SII6731 Flux. |
| 102 | `Flux_SII6731_Halpha_fitg` | fit flux unit | Halpha-region SII6731 Flux. |
| 103 | `Flux_OI6300_Halpha_fitl` | fit flux unit | Halpha-region OI6300 Flux. |
| 104 | `Flux_OI6300_Halpha_fitg` | fit flux unit | Halpha-region OI6300 Flux. |
| 105 | `Flux_OI6364_Halpha_fitl` | fit flux unit | Halpha-region OI6364 Flux. |
| 106 | `Flux_OI6364_Halpha_fitg` | fit flux unit | Halpha-region OI6364 Flux. |
| 107 | `Flux_Broad_Halpha_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region Broad_Halpha Flux. |
| 108 | `Flux_Broad_Halpha_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region Broad_Halpha Flux. Total summed broad profile. |
| 109 | `Flux_Narrow_Halpha_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region Narrow_Halpha Flux. |
| 110 | `Flux_Narrow_Halpha_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region Narrow_Halpha Flux. |
| 111 | `Flux_NII6548_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region NII6548 Flux. |
| 112 | `Flux_NII6548_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region NII6548 Flux. |
| 113 | `Flux_NII6583_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region NII6583 Flux. |
| 114 | `Flux_NII6583_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region NII6583 Flux. |
| 115 | `Flux_SII6716_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region SII6716 Flux. |
| 116 | `Flux_SII6716_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region SII6716 Flux. |
| 117 | `Flux_SII6731_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region SII6731 Flux. |
| 118 | `Flux_SII6731_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region SII6731 Flux. |
| 119 | `Flux_OI6300_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region OI6300 Flux. |
| 120 | `Flux_OI6300_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region OI6300 Flux. |
| 121 | `Flux_OI6364_Err_Halpha_fitl` | fit flux unit | Uncertainty on Halpha-region OI6364 Flux. |
| 122 | `Flux_OI6364_Err_Halpha_fitg` | fit flux unit | Uncertainty on Halpha-region OI6364 Flux. |
| 123 | `FWHM_Broad_Halpha_Halpha_fitl` | km s-1 | Halpha-region Broad_Halpha FWHM. |
| 124 | `FWHM_Broad_Halpha_Halpha_fitg` | km s-1 | Halpha-region Broad_Halpha FWHM. Total summed broad profile. |
| 125 | `FWHM_Narrow_Halpha_Halpha_fitl` | km s-1 | Halpha-region Narrow_Halpha FWHM. |
| 126 | `FWHM_Narrow_Halpha_Halpha_fitg` | km s-1 | Halpha-region Narrow_Halpha FWHM. |
| 127 | `FWHM_NII6548_Halpha_fitl` | km s-1 | Halpha-region NII6548 FWHM. |
| 128 | `FWHM_NII6548_Halpha_fitg` | km s-1 | Halpha-region NII6548 FWHM. |
| 129 | `FWHM_NII6583_Halpha_fitl` | km s-1 | Halpha-region NII6583 FWHM. |
| 130 | `FWHM_NII6583_Halpha_fitg` | km s-1 | Halpha-region NII6583 FWHM. |
| 131 | `FWHM_SII6716_Halpha_fitl` | km s-1 | Halpha-region SII6716 FWHM. |
| 132 | `FWHM_SII6716_Halpha_fitg` | km s-1 | Halpha-region SII6716 FWHM. |
| 133 | `FWHM_SII6731_Halpha_fitl` | km s-1 | Halpha-region SII6731 FWHM. |
| 134 | `FWHM_SII6731_Halpha_fitg` | km s-1 | Halpha-region SII6731 FWHM. |
| 135 | `FWHM_OI6300_Halpha_fitl` | km s-1 | Halpha-region OI6300 FWHM. |
| 136 | `FWHM_OI6300_Halpha_fitg` | km s-1 | Halpha-region OI6300 FWHM. |
| 137 | `FWHM_OI6364_Halpha_fitl` | km s-1 | Halpha-region OI6364 FWHM. |
| 138 | `FWHM_OI6364_Halpha_fitg` | km s-1 | Halpha-region OI6364 FWHM. |
| 139 | `FWHM_Broad_Halpha_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region Broad_Halpha FWHM. |
| 140 | `FWHM_Broad_Halpha_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region Broad_Halpha FWHM. Total summed broad profile. |
| 141 | `FWHM_Narrow_Halpha_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region Narrow_Halpha FWHM. |
| 142 | `FWHM_Narrow_Halpha_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region Narrow_Halpha FWHM. |
| 143 | `FWHM_NII6548_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region NII6548 FWHM. |
| 144 | `FWHM_NII6548_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region NII6548 FWHM. |
| 145 | `FWHM_NII6583_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region NII6583 FWHM. |
| 146 | `FWHM_NII6583_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region NII6583 FWHM. |
| 147 | `FWHM_SII6716_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region SII6716 FWHM. |
| 148 | `FWHM_SII6716_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region SII6716 FWHM. |
| 149 | `FWHM_SII6731_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region SII6731 FWHM. |
| 150 | `FWHM_SII6731_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region SII6731 FWHM. |
| 151 | `FWHM_OI6300_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region OI6300 FWHM. |
| 152 | `FWHM_OI6300_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region OI6300 FWHM. |
| 153 | `FWHM_OI6364_Err_Halpha_fitl` | km s-1 | Uncertainty on Halpha-region OI6364 FWHM. |
| 154 | `FWHM_OI6364_Err_Halpha_fitg` | km s-1 | Uncertainty on Halpha-region OI6364 FWHM. |
| 155 | `Flux_Broad_Halpha_G1_fitg` | fit flux unit | Flux_Broad_Halpha_G1 of the double-Gaussian Halpha model. |
| 156 | `Flux_Broad_Halpha_G2_fitg` | fit flux unit | Flux_Broad_Halpha_G2 of the double-Gaussian Halpha model. |
| 157 | `FWHM_Broad_Halpha_G1_fitg` | km s-1 | FWHM_Broad_Halpha_G1 of the double-Gaussian Halpha model. |
| 158 | `FWHM_Broad_Halpha_G2_fitg` | km s-1 | FWHM_Broad_Halpha_G2 of the double-Gaussian Halpha model. |
| 159 | `Broad_Halpha_G1_Fraction_fitg` | -- | Broad_Halpha_G1_Fraction of the double-Gaussian Halpha model. |
| 160 | `OIII5007_to_Narrow_Hbeta_BPT_fitl` | -- | Linear BPT ratio OIII5007_to_Narrow_Hbeta for the matched z<0.35 sample. |
| 161 | `OIII5007_to_Narrow_Hbeta_BPT_fitg` | -- | Linear BPT ratio OIII5007_to_Narrow_Hbeta for the matched z<0.35 sample. |
| 162 | `NII6583_to_Narrow_Halpha_BPT_fitl` | -- | Linear BPT ratio NII6583_to_Narrow_Halpha for the matched z<0.35 sample. |
| 163 | `NII6583_to_Narrow_Halpha_BPT_fitg` | -- | Linear BPT ratio NII6583_to_Narrow_Halpha for the matched z<0.35 sample. |
| 164 | `SII6716_6731_to_Narrow_Halpha_BPT_fitl` | -- | Linear BPT ratio SII6716_6731_to_Narrow_Halpha for the matched z<0.35 sample. |
| 165 | `SII6716_6731_to_Narrow_Halpha_BPT_fitg` | -- | Linear BPT ratio SII6716_6731_to_Narrow_Halpha for the matched z<0.35 sample. |
| 166 | `OI6300_to_Narrow_Halpha_BPT_fitl` | -- | Linear BPT ratio OI6300_to_Narrow_Halpha for the matched z<0.35 sample. |
| 167 | `OI6300_to_Narrow_Halpha_BPT_fitg` | -- | Linear BPT ratio OI6300_to_Narrow_Halpha for the matched z<0.35 sample. |
