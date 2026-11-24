# Research Documentation

This directory contains the scientific and methodological documentation for COSMIC ECHO.

The purpose of this documentation is to make the project's assumptions, analytical procedures, validation criteria, and limitations transparent.

## Documentation Structure

```text
docs/
│
├── README.md
├── methodology.md
└── validation.md
```

## Planned Documentation

### 1. Methodology

`methodology.md`

Will document:

- SPHEREx observation selection
- FITS data structure
- Image preprocessing
- Source detection
- Mask construction
- Background estimation
- Background subtraction
- Variance handling
- Processing parameters

### 2. Validation

`validation.md`

Will document:

- Validation objectives
- Statistical assumptions
- Variance-normalized diagnostics
- Spatial correlation analysis
- Multi-scale filtering
- Mask sensitivity
- Uncertainty considerations
- Known limitations

## Documentation Principles

The research documentation follows four principles:

**Transparency:** Explain the purpose and assumptions behind each analytical step.

**Reproducibility:** Record the data, parameters, software versions, and procedures used.

**Scientific caution:** Distinguish measured results from hypotheses and interpretations.

**Independent validation:** Evaluate methods using suitable reference data, alternative approaches, and critical review.

## Project Status

The documentation is being developed alongside the computational pipeline.

No method should be described as scientifically validated until its assumptions and performance have been adequately examined.