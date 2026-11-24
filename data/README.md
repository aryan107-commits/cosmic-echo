# Data Directory

This directory contains local observational data and intermediate computational products used by COSMIC ECHO.

Large datasets are intentionally excluded from Git version control.

## Directory Structure

```text
data/
│
├── raw/
│   └── first_spherex_image.fits
│
├── processed/
│   ├── quality_masks.npz
│   ├── photutils_background_v2.npz
│   └── other intermediate products
│
└── spherex_search_results.csv
```

*This is an illustrative structure. The actual files depend on the processing stage.*

## Data Sources

The project currently retrieves astronomical observations from the NASA/IPAC Infrared Science Archive (IRSA).

SPHEREx collections queried by the current workflow:

- `spherex_dr1`
- `spherex_qr3`

## Data Categories

### Raw Data

Original downloaded observational files, including FITS images and associated data layers.

These files should remain unchanged so that the original observations are preserved.

### Processed Data

Intermediate computational products generated during analysis.

Examples include:

- Background maps
- Background RMS maps
- Source masks
- Combined quality masks
- Corrected images
- Numerical validation outputs

### Metadata

Archive query results and observation metadata are stored separately from the original image data.

## Retrieval

Run the archive query:

```bash
python scripts/query_spherex.py
```

Then download the selected observation:

```bash
python scripts/download_spherex.py
```

## Data Management Policy

The repository excludes local research data to avoid:

- Unnecessarily large Git history
- Accidental uploads of large observational files
- Duplication of publicly available datasets
- Confusion between source observations and derived products

The data directory is ignored by Git. Users must retrieve the required files locally before running the analysis scripts.

## Data Integrity

Original observations should not be overwritten by processing scripts.

Derived products should be stored separately, with processing steps and parameters documented wherever possible.