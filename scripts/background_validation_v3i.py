import numpy as np
from scipy.ndimage import gaussian_filter
from astropy.io import fits

print("\nCOSMIC ECHO | V3I CORRELATION PROFILE")
print("=" * 70)

with fits.open("data/raw/first_spherex_image.fits") as hdul:
    variance = hdul["VARIANCE"].data.astype(float)

data = np.load("data/processed/photutils_background_v2.npz")

corrected = data["corrected"]
combined_mask = data["combined_mask"].astype(bool)

valid = (
    np.isfinite(corrected)
    & np.isfinite(variance)
    & (variance > 0)
    & (~combined_mask)
)

sigma = np.sqrt(variance)

z = np.full(corrected.shape, np.nan)
z[valid] = corrected[valid] / sigma[valid]

filled = np.where(valid, z, 0.0)
weights = valid.astype(float)


def robust_sigma(values):
    values = values[np.isfinite(values)]
    med = np.median(values)
    return 1.4826 * np.median(np.abs(values - med))


def correlation_at_lag(array, mask, axis, lag):
    if axis == 1:
        a = (slice(None), slice(None, -lag))
        b = (slice(None), slice(lag, None))
    else:
        a = (slice(None, -lag), slice(None))
        b = (slice(lag, None), slice(None))

    good = mask[a] & mask[b]

    x = array[a][good]
    y = array[b][good]

    if len(x) < 100:
        return np.nan

    return np.corrcoef(x, y)[0, 1]


print("\nSCALE-WISE CORRELATION PROFILE")

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

    print(f"\nGaussian scale: {scale} pixels")
    print("Lag | Horizontal | Vertical")

    for lag in [1, 2, 4, 8, 16, 32]:
        h = correlation_at_lag(
            highpass, highpass_valid, 1, lag
        )
        v = correlation_at_lag(
            highpass, highpass_valid, 0, lag
        )

        print(f"{lag:3d} | {h:10.4f} | {v:8.4f}")

    print(
        "High-pass robust scatter:",
        round(robust_sigma(highpass[highpass_valid]), 4)
    )

print("\nV3I COMPLETE")
