
import numpy as np
from astropy.io import fits
from pathlib import Path

# -----------------------------------------
# COSMIC ECHO | QUANTITATIVE VALIDATION V3
# -----------------------------------------

print("\nCOSMIC ECHO | V3 QUANTITATIVE VALIDATION")
print("-" * 50)

# Load original image
with fits.open("data/raw/first_spherex_image.fits") as hdul:
    original = hdul["IMAGE"].data.astype(float)

# Load V2 products
data = np.load("data/processed/photutils_background_v2.npz")

background = data["background_map"]
rms = data["background_rms"]
corrected = data["corrected"]
source_mask = data["source_mask"].astype(bool)
combined_mask = data["combined_mask"].astype(bool)

# Valid unmasked sky pixels
valid = (
    np.isfinite(original)
    & np.isfinite(background)
    & np.isfinite(rms)
    & np.isfinite(corrected)
    & (rms > 0)
    & (~combined_mask)
)

residual = corrected[valid]
normalized = residual / rms[valid]
estimated_rms = rms[valid]

if residual.size == 0:
    raise ValueError("No valid unmasked pixels available.")

# Robust statistics
def robust_sigma(values):
    median = np.median(values)
    return 1.4826 * np.median(np.abs(values - median))

residual_median = np.median(residual)
residual_sigma = robust_sigma(residual)

normalized_median = np.median(normalized)
normalized_sigma = robust_sigma(normalized)

rms_median = np.median(estimated_rms)

# Mask coverage
base_coverage = 1 - np.mean(valid)
source_coverage = np.mean(source_mask)
combined_coverage = np.mean(combined_mask)

# Report
print("\nPIXEL STATISTICS")
print("Total pixels:", original.size)
print("Valid sky pixels:", residual.size)
print("Excluded pixels:", original.size - residual.size)

print("\nMASK COVERAGE")
print(f"Source mask: {source_coverage * 100:.3f}%")
print(f"Combined mask: {combined_coverage * 100:.3f}%")
print(f"Excluded from validation: {base_coverage * 100:.3f}%")

print("\nBACKGROUND RESIDUAL")
print(f"Median: {residual_median:.8f}")
print(f"Robust sigma: {residual_sigma:.8f}")
print(f"Median estimated RMS: {rms_median:.8f}")

print("\nNORMALIZED RESIDUAL")
print(f"Median: {normalized_median:.6f}")
print(f"Robust sigma: {normalized_sigma:.6f}")

print("\nRESIDUAL PERCENTILES")
for p in [1, 5, 25, 50, 75, 95, 99]:
    print(f"{p}th percentile: {np.percentile(residual, p):.6f}")

# Spatial validation in 10 x 10 tiles
print("\nSPATIAL BACKGROUND VALIDATION")

tile_size = 204

tile_medians = []

for y in range(0, 2040, tile_size):
    for x in range(0, 2040, tile_size):

        tile_valid = valid[
            y:y + tile_size,
            x:x + tile_size
        ]

        tile_residual = corrected[
            y:y + tile_size,
            x:x + tile_size
        ][tile_valid]

        if tile_residual.size >= 100:
            tile_medians.append(np.median(tile_residual))

tile_medians = np.array(tile_medians)

if tile_medians.size:
    print("Valid tiles:", tile_medians.size)
    print("Tile median residual:", np.median(tile_medians))
    print("Tile-to-tile robust sigma:", robust_sigma(tile_medians))
else:
    print("Insufficient valid tiles.")

# Save machine-readable report
output = Path("data/processed/v3_validation_report.npz")

np.savez_compressed(
    output,
    residual_median=residual_median,
    residual_sigma=residual_sigma,
    normalized_median=normalized_median,
    normalized_sigma=normalized_sigma,
    median_estimated_rms=rms_median,
    tile_medians=tile_medians,
    valid_pixel_count=residual.size
)

print("\nReport saved:", output)
print("\nV3 QUANTITATIVE VALIDATION COMPLETE")
