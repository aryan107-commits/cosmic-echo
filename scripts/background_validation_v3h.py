
import numpy as np
from scipy.ndimage import gaussian_filter
from astropy.io import fits

print("\nCOSMIC ECHO | V3H STRUCTURE SEPARATION")
print("=" * 65)

with fits.open("data/raw/first_spherex_image.fits") as hdul:
    variance = hdul["VARIANCE"].data.astype(float)
    flags = hdul["FLAGS"].data.astype(np.uint32)

data = np.load("data/processed/photutils_background_v2.npz")

corrected = data["corrected"]
combined_mask = data["combined_mask"].astype(bool)

valid = (
    np.isfinite(corrected)
    & np.isfinite(variance)
    & (variance > 0)
    & (~combined_mask)
)

sigma = np.sqrt(np.maximum(variance, 0))

# Normalized residual
z = np.full(corrected.shape, np.nan)
z[valid] = corrected[valid] / sigma[valid]

# Fill invalid pixels with zero only for filtering.
# A separate smoothed validity map corrects for missing coverage.
filled = np.where(valid, z, 0.0)
weights = valid.astype(float)

def robust_sigma(values):
    values = values[np.isfinite(values)]
    med = np.median(values)
    return 1.4826 * np.median(np.abs(values - med))

def correlation_at_lag(array, valid_mask, axis, lag):
    if axis == 1:
        a = (slice(None), slice(None, -lag))
        b = (slice(None), slice(lag, None))
    else:
        a = (slice(None, -lag), slice(None))
        b = (slice(lag, None), slice(None))

    good = valid_mask[a] & valid_mask[b]

    x = array[a][good]
    y = array[b][good]

    return np.corrcoef(x, y)[0, 1]

print("\nMASK OVERLAP")
quality_bits = [0, 1, 2, 6, 9, 10, 11, 15, 17, 19, 20,
                22, 23, 24, 25, 26, 27, 28]

quality_mask = np.zeros(flags.shape, dtype=bool)

for bit in quality_bits:
    quality_mask |= (
        flags & (np.uint32(1) << np.uint32(bit))
    ) != 0

print("Quality mask coverage:", quality_mask.mean() * 100)
print("Quality outside combined:", np.mean(
    quality_mask & ~combined_mask
) * 100)

# Test broad spatial structures at different scales.
print("\nSTRUCTURE REMOVAL TEST")
print("Scale | Horizontal correlation | Vertical correlation | Robust scatter")

for scale in [8, 16, 32]:
    smooth_values = gaussian_filter(filled, sigma=scale)
    smooth_weights = gaussian_filter(weights, sigma=scale)

    smooth = np.full(z.shape, np.nan)

    good_smooth = smooth_weights > 0.5
    smooth[good_smooth] = (
        smooth_values[good_smooth] / smooth_weights[good_smooth]
    )

    highpass = z - smooth

    highpass_valid = valid & np.isfinite(highpass)

    h = correlation_at_lag(highpass, highpass_valid, 1, 1)
    v = correlation_at_lag(highpass, highpass_valid, 0, 1)

    print(
        f"{scale:5d} | {h:23.4f} | {v:20.4f} | "
        f"{robust_sigma(highpass[highpass_valid]):.4f}"
    )

print("\nV3H COMPLETE")
