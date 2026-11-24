# Scripts and Computational Workflows

This directory contains the Python scripts used in the COSMIC ECHO project.

The scripts cover astronomical data retrieval, image processing, background estimation, mask analysis, and statistical diagnostics.

## Script Catalogue

| Script | Purpose |
|---|---|
| `query_spherex.py` | Queries SPHEREx observations through IRSA |
| `download_spherex.py` | Downloads a selected FITS observation |
| `photutils_background_v2.py` | Estimates and subtracts the image background |
| `audit_mask_decomposition.py` | Audits mask layers and image quality |
| `background_validation_v3i.py` | Performs variance-aware, multi-scale correlation analysis |

## Execution Workflow

### 1. Query the SPHEREx archive

```bash
python scripts/query_spherex.py
```

Expected output:

```text
data/spherex_search_results.csv
```

### 2. Download an observation

```bash
python scripts/download_spherex.py
```

Expected output:

```text
data/raw/first_spherex_image.fits
```

### 3. Background estimation

```bash
python scripts/photutils_background_v2.py
```

This script expects its required FITS and mask inputs to exist locally.

### 4. Mask decomposition audit

```bash
python scripts/audit_mask_decomposition.py
```

Check the script's command-line options and input requirements before execution.

### 5. Statistical validation

```bash
python scripts/background_validation_v3i.py
```

This workflow examines variance-normalized image values and spatial correlation profiles at multiple filtering scales.

## Dependencies

The current scripts use:

- NumPy
- SciPy
- Astropy
- Photutils
- Astroquery
- Pandas
- Matplotlib

Install them with:

```bash
python -m pip install numpy scipy astropy photutils astroquery pandas matplotlib
```

## Development Principles

The scripts are being developed around the following principles:

1. Reproducible computational procedures.
2. Explicit input and output requirements.
3. Traceable intermediate products.
4. Statistical diagnostics rather than visual inspection alone.
5. Clear separation between measurements and scientific interpretation.

## Important Notes

- Input data are not included in this repository.
- Several scripts currently use fixed local file paths.
- Execution order depends on the availability of intermediate files.
- Scientific conclusions should not be inferred solely from successful script execution.

The computational workflow is under active development.