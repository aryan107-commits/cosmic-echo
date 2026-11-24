# COSMIC ECHO

### Exploring the structure behind astronomical observations

**COSMIC ECHO** is an independent scientific computing project focused on the analysis of astronomical imaging data from NASA's SPHEREx mission.

The project investigates image-background estimation, source masking, variance-aware diagnostics, and statistical validation through reproducible Python workflows.

<p align="center">
  <strong>ASTRONOMY · SCIENTIFIC COMPUTING · IMAGE ANALYSIS</strong>
</p>

---

## Research Overview

Astronomical images contain more than the celestial sources being observed. Background emission, instrumental effects, and observational noise can influence the interpretation of image data.

COSMIC ECHO aims to develop and evaluate computational methods for examining these components.

### Current research directions

- SPHEREx archive exploration and FITS data retrieval
- Spatially varying background estimation
- Astronomical source detection and masking
- Quality-mask decomposition
- Variance-aware image diagnostics
- Multi-scale spatial correlation analysis

## Research Pipeline

```text
SPHEREx Archive
      |
      v
Observation Retrieval
      |
      v
FITS Inspection
      |
      v
Quality Assessment
      |
      v
Source Detection & Masking
      |
      v
Background Estimation
      |
      v
Background Correction
      |
      v
Statistical Validation
```

*This represents the intended analytical workflow; individual stages are at different levels of implementation.*

## Technology

| Domain | Tools |
|---|---|
| Programming | Python |
| Numerical analysis | NumPy, SciPy |
| Astronomy | Astropy, Astroquery |
| Image processing | Photutils |
| Data handling | Pandas |
| Visualization | Matplotlib |

## Repository Navigation

| Directory | Description |
|---|---|
| `scripts/` | Analysis and data-retrieval scripts |
| `data/` | Local observational and processed data |
| `docs/` | Research methodology and validation documentation |

## Current Development

The current implementation includes:

- SPHEREx archive query and observation retrieval
- FITS data inspection
- Photutils-based background estimation
- Source and quality-mask analysis
- Mask decomposition auditing
- Multi-scale correlation diagnostics

The project is under active development. Quantitative findings and scientific interpretations require further validation.

## Reproducibility

Large observational files and intermediate numerical products are excluded from Git.

To begin, clone the repository:

```bash
git clone https://github.com/aryan107-commits/cosmic-echo.git
cd cosmic-echo
```

Install the current dependencies:

```bash
python -m pip install numpy scipy matplotlib astropy photutils astroquery pandas
```

See [`scripts/README.md`](scripts/README.md) for the current script workflow and [`data/README.md`](data/README.md) for data organization.

## Scientific Integrity

COSMIC ECHO distinguishes computational implementation from scientific conclusions.

A successful execution is not sufficient evidence of scientific validity. Methods, assumptions, uncertainty estimates, and limitations must be independently examined.

## Author

**Aryan Verma**

Engineering · Scientific Computing · Mathematical Problem-Solving

[GitHub Profile](https://github.com/aryan107-commits)

---

*COSMIC ECHO — Exploring the structure behind astronomical observations.*