# DESI DR1 Type 1 AGN Catalog

**v1.1.0 — Publication Catalog**

This catalog accompanies **Yao et al. (2026)**,
[The Population of Type 1 Active Galactic Nuclei in Dark Energy Spectroscopic Instrument. I. Profile-dependent Measurements of the Low-redshift Sample](https://arxiv.org/abs/2610.13218).

## Contents

The catalog contains **114,754 Type 1 AGNs at z ≤ 0.9**, with **266 columns** in the `TYPE1_CATALOG` FITS extension. It provides:

- DESI target identifiers, redshifts, continuum signal-to-noise ratios, and 4000 Å break indices.
- Host-subtracted 5100 Å luminosities.
- Continuum and emission-line measurements from Lorentzian (`fitl`) and double-Gaussian (`fitg`) fits, including fluxes, widths, velocity shifts, luminosities, equivalent widths, and line ratios.
- Broad-line-region radii, black hole masses, dimensionless mass accretion rates, and measurement uncertainties.
- NLS1 classification flags: **25,603** objects selected with Lorentzian fits, **13,491** with double-Gaussian fits, and **12,036** with both.
- Hα-region measurements and BPT line ratios for **15,390** sources at z < 0.35.

Uncertainty columns end with `_Err`. Integrated fluxes are in units of **10⁻¹⁷ erg s⁻¹ cm⁻²**, and continuum flux densities are in **10⁻¹⁷ erg s⁻¹ cm⁻² Å⁻¹**. FWHMs and velocity shifts are in **km s⁻¹**, luminosities in **erg s⁻¹**, and black hole masses in **solar masses**. Missing measurements are represented by NaN; some legacy missing break-index values are stored as zero.

## Usage

Download the FITS file from [Releases](https://github.com/yao-astro/DESIDR1-type1AGNcat/releases) and read it with [Astropy](https://www.astropy.org/):

```bash
pip install astropy
```

```python
from astropy.table import Table

# Set this path to your downloaded FITS file.
filename = "desidr1_type1cat_yao2026.fits"
cat = Table.read(filename, hdu="TYPE1_CATALOG")

print(len(cat), len(cat.colnames))
print(cat["TARGETID", "Z", "L5100"][:5])

# Select NLS1s identified by both fitting schemes.
nls1 = cat[cat["NLS1FLAG_BOTH"] == 1]

# Access a measurement and its uncertainty.
fwhm = cat["FWHM_BroadHbeta_fitg"]
fwhm_err = cat["FWHM_BroadHbeta_fitg_Err"]

# Convert an integrated line flux to erg s^-1 cm^-2.
flux_oiii5007 = cat["Flux_OIII5007_fitl"] * 1e-17
```

For each fitting scheme, NLS1 selection requires `FWHM - FWHM_Err < 2000 km/s` and `FWHM < 2200 km/s`. Flags are `1` for selected objects, `0` for unselected objects, and `-1` for unavailable classification inputs.

## Citation

If you use this catalog, please cite the paper (arXiv: [2610.13218](https://arxiv.org/abs/2610.13218)).
