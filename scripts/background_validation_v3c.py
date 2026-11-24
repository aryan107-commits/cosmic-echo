
import numpy as np
from astropy.io import fits

print("\nCOSMIC ECHO | V3C SPATIAL NOISE INVESTIGATION")
print("-" * 55)

# Load original FITS data and metadata
with fits.open("data/raw/first_spherex_image.fits") as hdul:
    original = hdul["IMAGE"].data.astype(float)
    header = hdul["IMAGE"].header

# Load V2 products
data = np.load("data/processed/photutils_background_v2.npz")

background = data["background_map"]
rms = data["background_rms"]
corrected = data["corrected"]
mask = data["combined_mask"].astype(bool)

valid = (
    np.isfinite(original)
    & np.isfinite(background)
    & np.isfinite(rms)
    & np.isfinite(corrected)
    & (rms > 0)
    & (~mask)
)

normalized = np.full(original.shape, np.nan)
normalized[valid] = corrected[valid] / rms[valid]

def robust_sigma(values):
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan
    median = np.median(values)
    return 1.4826 * np.median(np.abs(values - median))

print("\nFITS METADATA")
for key in ["BUNIT", "TELESCOP", "INSTRUME", "FILTER", "WAVELEN"]:
    print(f"{key}: {header.get(key, 'Not available')}")

print("\nIMAGE VALIDITY")
print("Image shape:", original.shape)
print("Valid pixels:", np.sum(valid))
print("Invalid or masked:", np.size(valid) - np.sum(valid))

# -------------------------------------
# 1. TILE-BY-TILE NOISE ANALYSIS
# -------------------------------------

print("\nTILE NOISE ANALYSIS")
print("-" * 40)

tile_size = 204
tile_sigmas = []
tile_medians = []
tile_coverages = []

for y in range(0, original.shape[0], tile_size):
    for x in range(0, original.shape[1], tile_size):

        tile_valid = valid[
            y:y + tile_size,
            x:x + tile_size
        ]

        tile = normalized[
            y:y + tile_size,
            x:x + tile_size
        ]

        values = tile[tile_valid]

        coverage = np.mean(tile_valid)
        tile_coverages.append(coverage)

        if values.size >= 100:
            tile_sigmas.append(robust_sigma(values))
            tile_medians.append(np.median(values))
        else:
            tile_sigmas.append(np.nan)
            tile_medians.append(np.nan)

tile_sigmas = np.array(tile_sigmas)
tile_medians = np.array(tile_medians)
tile_coverages = np.array(tile_coverages)

good = np.isfinite(tile_sigmas)

print("Total tiles:", len(tile_sigmas))
print("Usable tiles:", np.sum(good))
print("Median tile normalized sigma:",
      np.nanmedian(tile_sigmas))
print("Tile sigma spread:",
      robust_sigma(tile_sigmas[good]))
print("Tile median normalized residual:",
      np.nanmedian(tile_medians))
print("Median tile coverage:",
      np.median(tile_coverages) * 100, "%")

print("\nTILE EXTREMES")

if np.any(good):
    print("Lowest tile sigma:", np.nanmin(tile_sigmas))
    print("Highest tile sigma:", np.nanmax(tile_sigmas))

# -------------------------------------
# 2. SPATIAL CORRELATION
# -------------------------------------

print("\nSPATIAL CORRELATION ANALYSIS")

# Remove each tile's local median before measuring
# neighbouring-pixel correlation.
centered = np.full(normalized.shape, np.nan)

for y in range(0, original.shape[0], tile_size):
    for x in range(0, original.shape[1], tile_size):

        tile = normalized[
            y:y + tile_size,
            x:x + tile_size
        ]

        tile_valid = valid[
            y:y + tile_size,
            x:x + tile_size
        ]

        values = tile[tile_valid]

        if values.size >= 100:
            centered_tile = centered[
                y:y + tile_size,
                x:x + tile_size
            ]

            centered_tile[tile_valid] = (
                values - np.median(values)
            )

def neighbor_correlation(a, b, mask_a, mask_b):
    good = (
        mask_a & mask_b
        & np.isfinite(a) & np.isfinite(b)
    )

    if np.sum(good) < 1000:
        return np.nan

    return np.corrcoef(a[good], b[good])[0, 1]

corr_x = neighbor_correlation(
    centered[:, :-1],
    centered[:, 1:],
    valid[:, :-1],
    valid[:, 1:]
)

corr_y = neighbor_correlation(
    centered[:-1, :],
    centered[1:, :],
    valid[:-1, :],
    valid[1:, :]
)

print("Horizontal lag-1 correlation:", corr_x)
print("Vertical lag-1 correlation:", corr_y)

# -------------------------------------
# 3. BACKGROUND RMS COMPARISON
# -------------------------------------

print("\nRMS COMPARISON")

residual_sigma = robust_sigma(corrected[valid])
rms_median = np.median(rms[valid])

print("Residual robust sigma:", residual_sigma)
print("Median estimated RMS:", rms_median)
print("Ratio:", residual_sigma / rms_median)

# -------------------------------------
# 4. SAVE RESULTS
# -------------------------------------

np.savez_compressed(
    "data/processed/v3c_spatial_report.npz",
    tile_sigmas=tile_sigmas,
    tile_medians=tile_medians,
    tile_coverages=tile_coverages,
    horizontal_correlation=corr_x,
    vertical_correlation=corr_y,
    residual_sigma=residual_sigma,
    rms_median=rms_median
)

print("\nReport saved:")
print("data/processed/v3c_spatial_report.npz")

print("\nV3C INVESTIGATION COMPLETE")
