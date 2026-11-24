
import numpy as np
from astropy.io import fits

print("\nCOSMIC ECHO | V3E VARIANCE VALIDATION")
print("=" * 60)

fits_path = "data/raw/first_spherex_image.fits"
npz_path = "data/processed/photutils_background_v2.npz"

# Load the original FITS extensions
with fits.open(fits_path) as hdul:
    image = hdul["IMAGE"].data.astype(float)
    flags = hdul["FLAGS"].data
    variance = hdul["VARIANCE"].data.astype(float)
    zodi = hdul["ZODI"].data.astype(float)

# Load Photutils outputs
data = np.load(npz_path)
background_rms = data["background_rms"]
corrected = data["corrected"]
combined_mask = data["combined_mask"].astype(bool)

# Basic validation
print("\nARRAY VALIDATION")
for name, array in [
    ("IMAGE", image),
    ("VARIANCE", variance),
    ("FLAGS", flags),
    ("ZODI", zodi),
    ("BACKGROUND RMS", background_rms),
    ("CORRECTED", corrected),
]:
    print(
        f"{name:16s}",
        "shape =", array.shape,
        "| finite =", np.isfinite(array).mean() * 100, "%"
    )

# Derive uncertainty from variance
valid_variance = np.isfinite(variance) & (variance > 0)
variance_rms = np.full(variance.shape, np.nan)
variance_rms[valid_variance] = np.sqrt(variance[valid_variance])

# Compare uncertainty maps
valid = (
    valid_variance
    & np.isfinite(background_rms)
    & (background_rms > 0)
    & (~combined_mask)
)

ratio = variance_rms[valid] / background_rms[valid]

print("\nVARIANCE VS PHOTUTILS RMS")
print("Comparable pixels:", ratio.size)

for name, values in [
    ("Variance-derived RMS", variance_rms[valid]),
    ("Photutils RMS", background_rms[valid]),
    ("Ratio: sqrt(variance) / Photutils RMS", ratio),
]:
    print(f"\n{name}")
    print("Median:", np.median(values))
    print("16th percentile:", np.percentile(values, 16))
    print("84th percentile:", np.percentile(values, 84))

# Check whether the supplied variance predicts corrected residuals
normalized = corrected[valid] / variance_rms[valid]

median = np.median(normalized)
robust_sigma = 1.4826 * np.median(np.abs(normalized - median))

print("\nCORRECTED IMAGE / VARIANCE-DERIVED RMS")
print("Median:", median)
print("Robust sigma:", robust_sigma)
print("Percentiles:", np.percentile(normalized, [1, 5, 50, 95, 99]))

# Inspect quality flags
print("\nFLAG VALUE COUNTS")
unique, counts = np.unique(flags, return_counts=True)

for value, count in zip(unique[:40], counts[:40]):
    print(
        f"Flag {value}: {count:,} pixels "
        f"({100 * count / flags.size:.3f}%)"
    )

if len(unique) > 40:
    print("Additional distinct flag values:", len(unique) - 40)

# Zodiacal light statistics
valid_zodi = np.isfinite(zodi)

print("\nZODI STATISTICS")
print("Valid pixels:", valid_zodi.sum())
print("Median:", np.median(zodi[valid_zodi]))
print("Minimum:", np.min(zodi[valid_zodi]))
print("Maximum:", np.max(zodi[valid_zodi]))

print("\nV3E VALIDATION COMPLETE")
