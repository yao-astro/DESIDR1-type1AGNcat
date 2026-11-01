# DESI DR1 Type 1 AGN catalogue

This is the machine-readable catalogue accompanying **Yao et al. (2026)**, \
[The Population of Type 1 Active Galactic Nuclei in Dark Energy Spectroscopic Instrument. I. Profile-dependent Measurements of the Low-redshift Sample](https://arxiv.org/abs/2610.13218).\
It contains **114,754 Type 1 active galactic nuclei (AGNs) at z ≤ 0.9** selected
from the first data release of the Dark Energy Spectroscopic Instrument
(DESI DR1). The catalogue provides DESI target identifiers and redshifts,
continuum signal-to-noise ratios and 4000 Å break indices, host-subtracted
5100 Å luminosities, emission-line measurements from Lorentzian and
double-Gaussian broad-line fits, Fe II strengths, narrow-line Seyfert 1
(NLS1) classification flags, and estimates of black-hole mass and
dimensionless accretion rate. Hα-region measurements and BPT emission-line
ratios are included for **15,390 sources at z < 0.35**. The main table has
one row per source and **167 columns**, following Table 2 of the paper.

## Reading the catalogue

The data are provided in **`desidr1_type1cat.fits`**. All measurements,
flux conversion factors, and column descriptions are contained in this
single FITS file.

Install Astropy if needed:

```bash
python3 -m pip install astropy
```

Run the following Python example in the directory containing the FITS file,
or replace the filename with its full path:

```python
from astropy.io import fits
from astropy.table import Table

with fits.open("desidr1_type1cat.fits", memmap=False) as hdul:
    catalog = Table.read(hdul, hdu="TYPE1_CATALOG")
    scales = Table.read(hdul, hdu="FLUX_SCALE")
    columns = Table.read(hdul, hdu="COLUMN_INFO")

print(f"{len(catalog):,} sources, {len(catalog.colnames)} columns")
print(catalog["TARGETID", "Z", "L5100"][:5])

# Select objects classified as NLS1s under both broad-line models.
nls1_both = catalog[catalog["NLS1_FLAG_BOTH"] == 1]
print(f"{len(nls1_both):,} NLS1s in both models")

# Select a source using its exact integer TARGETID.
target = catalog[catalog["TARGETID"] == 39627884268098267]

# Inspect a column definition.
print(columns[columns["COLUMN"] == "MBH_fitg"])

# Convert the Lorentzian [O III] 5007 line flux to erg s^-1 cm^-2.
flux_oiii5007 = catalog["Flux_OIII5007_fitl"] * scales["UNIT_fitl"] * 1e-17
```

## FITS structure

| Extension | Content |
|---|---|
| `PRIMARY` | General catalogue metadata. |
| `TYPE1_CATALOG` | The main catalogue: 114,754 sources and 167 columns corresponding to Table 2. |
| `FLUX_SCALE` | Per-source factors for converting fitted fluxes to physical units. |
| `COLUMN_INFO` | Column names, units, data types, descriptions, and numbers of missing measurements. |
| `PROVENANCE` | Records identifying the data products used to assemble the catalogue. |

`TYPE1_CATALOG` and `FLUX_SCALE` have identical TARGETID order, sorted numerically.
TARGETID is a signed 64-bit integer (FITS `K`), never a floating-point number.
Measurements are 64-bit floats (`D`). Missing measurements are stored as NaN
and may appear as masked entries (`--`) when read with Astropy. Zero values,
including zero uncertainties, are retained as recorded.

## Profiles and classification

The column suffix `fitl` denotes a Lorentzian broad-line model, and `fitg`
denotes a broad-line model consisting of **two Gaussian components**.
`BROAD_PROFILE_fitl` and `BROAD_PROFILE_fitg` store `lorentzian` and
`dgaussian`, respectively. For the double-Gaussian fits, the total broad-line
flux is G1+G2, and the broad-line FWHM describes their summed profile.

For each profile, `NLS1_FLAG=1` requires both

```
FWHM_Broad_Hbeta - FWHM_Broad_Hbeta_Err < 2000 km/s
FWHM_Broad_Hbeta < 2200 km/s
```

Widths must be finite and positive, and errors finite and nonnegative.
Flag `0` means the criterion is not met; `-1` means the inputs are invalid.
`NLS1_FLAG_BOTH=1` requires both profile flags to be 1, `-1` means either
profile is unclassifiable, and 0 covers the remaining cases.

| Selection | Count |
|---|---:|
| All Type 1 AGNs | 114,754 |
| NLS1, Lorentzian | 25,628 |
| NLS1, two Gaussians | 13,359 |
| NLS1 in both | 11,012 |
| Invalid two-Gaussian classification inputs | 3 |
| Hα/BPT measurement coverage (z < 0.35) | 15,390 |

Hα/BPT measurements are NaN outside the 15,390-source z < 0.35 subset.
Within that subset, individual derived ratios may also be unavailable.
The BPT ratios are linear, and the [S II] numerator is the sum of 6716 and 6731.
The non-BPT [O III]/narrow-Hβ columns allow a finite zero numerator;
the BPT ratios require
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

For 112,853 Lorentzian fits, the flux scale is set to 1 following the
convention used to calculate the published line luminosities. These entries
are identified by `FLUX_SCALE.UNIT_DEFAULT_fitl=1`.

`L5100` and its errors come from the host-subtracted continuum product.
`D4000` and `Dn4000` are the original spectrum/product indices, not the
separately measured host-only indices. EWs are in rest-frame Angstrom.

## Black-hole mass and accretion rate

`MBH_<prof>` is the black-hole mass in solar masses, and `mdot_<prof>` is
the dimensionless mass-accretion-rate estimate. Both are stored as linear
values. They use the Fe II-dependent radius-luminosity relation adopted in
the paper, with the common host-subtracted `L5100` and each model's RFe:

```
log10(R_Hbeta / light-day) = 1.65 + 0.45*log10(L5100/1e44) - 0.35*RFe
MBH = 0.75 * R_Hbeta * FWHM^2 / G          (converted to solar masses)
mdot = 20.1 * ((L5100/1e44)/0.75)^1.5 * (MBH/1e7)^(-2)
```

`mdot` is a dimensionless mass-accretion-rate proxy, not Lbol/Ledd.

**Numerical convention for the double-Gaussian model:** the tabulated
`FWHM_Broad_Hbeta_fitg` uses a 501-point velocity grid, whereas `MBH_fitg`
and `mdot_fitg` were calculated using a width re-evaluated on a 1,201-point
grid. Inserting the tabulated width into the mass formula therefore does
not always reproduce `MBH_fitg`: the median absolute difference is
0.003526 dex, 1,157 sources differ by more than 0.1 dex, and the largest
difference is 3.9601 dex. The catalogue retains the measurements used in the
paper. Zero uncertainties and parameters at fitting bounds should not be
interpreted as exact measurements.

## Column descriptions

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

## Citation

If you use this catalog, please cite the paper (arXiv: [2610.13218](https://arxiv.org/abs/2610.13218)).
