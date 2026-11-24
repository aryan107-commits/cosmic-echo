
import numpy as np
from astropy.io import fits

print("\nCOSMIC ECHO | V3G SPATIAL CORRELATION TEST")
print("=" * 65)

with fits.open("data/raw/first_spherex_image.fits") as hdul:
    flags = hdul["FLAGS"].data.astype(np.uint32)
    variance = hdul["VARIANCE"].data.astype(float)

data = np.load("data/processed/photutils_background_v2.npz")

corrected = data["corrected"]
combined_mask = data["combined_mask"].astype(bool)

# Exclude selected quality/artifact flags.
# SOURCE (bit 21) is deliberately NOT excluded.
# FULLSAMPLE (bit 12) is also not treated as a bad-pixel flag.

exclude_bits = [
    0, 1, 2, 6, 9, 10, 11, 15, 17, 19, 20,
    22, 23, 24, 25, 26, 27, 28
]

quality_mask = np.zeros(flags.shape, dtype=bool)

for bit in exclude_bits:
    quality_mask |= (
        flags & (np.uint32(1) << np.uint32(bit))
    ) != 0

valid = (
    np.isfinite(corrected)
    & np.isfinite(variance)
    & (variance > 0)
    & (~combined_mask)
    & (~quality_mask)
)

print("\nMASK COVERAGE")
print("Combined mask:", combined_mask.mean() * 100, "%")
print("Quality flag mask:", quality_mask.mean() * 100, "%")
print("Final valid pixels:", valid.sum())

def robust_sigma(values):
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan
    median = np.median(values)
    return 1.4826 * np.median(np.abs(values - median))

def test_direction(axis, lag, label):
    if axis == 1:
        a = (slice(None), slice(None, -lag))
        b = (slice(None), slice(lag, None))
    else:
        a = (slice(None, -lag), slice(None))
        b = (slice(lag, None), slice(None))

    pair_valid = valid[a] & valid[b]

    r1 = corrected[a][pair_valid]
    r2 = corrected[b][pair_valid]

    v1 = variance[a][pair_valid]
    v2 = variance[b][pair_valid]

    denominator = np.sqrt(v1 + v2)

    normalized_difference = (r1 - r2) / denominator

    n1 = r1 / np.sqrt(v1)
    n2 = r2 / np.sqrt(v2)

    # Pearson correlation is included as a diagnostic,
    # not as a standalone proof of instrumental correlation.
    correlation = np.corrcoef(n1, n2)[0, 1]

    print(
        f"{label:10s} lag={lag:<2d} "
        f"pairs={pair_valid.sum():>9,} "
        f"diff_sigma={robust_sigma(normalized_difference):.4f} "
        f"correlation={correlation:.4f}"
    )

print("\nNEIGHBOUR DIFFERENCE TEST")
print("Direction | Lag | Valid pairs | Robust scatter | Correlation")

for lag in [1, 2, 4, 8]:
    test_direction(1, lag, "Horizontal")
    test_direction(0, lag, "Vertical")

print("\nV3G COMPLETE")
