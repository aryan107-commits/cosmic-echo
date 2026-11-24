
import numpy as np
import pandas as pd

from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import maximum_filter

IMAGE_FILE = "data/raw/first_spherex_image.fits"
MASK_FILE = "data/processed/quality_masks.npz"

with fits.open(IMAGE_FILE) as hdul:
    image = hdul["IMAGE"].data.astype(float)
    variance = hdul["VARIANCE"].data.astype(float)
    wcs = WCS(hdul["IMAGE"].header)

with np.load(MASK_FILE) as masks:
    hard_mask = masks["hard_mask"]

# Valid measurements only
valid = (
    np.isfinite(image)
    & np.isfinite(variance)
    & (variance > 0)
    & ~hard_mask
)

# Signal-to-noise map
snr = np.full(image.shape, np.nan)
snr[valid] = image[valid] / np.sqrt(variance[valid])

# Local maxima: preliminary candidate detections
snr_for_detection = np.where(valid, snr, -np.inf)

local_max = maximum_filter(
    snr_for_detection,
    size=5
)

threshold = 5.0

detections = (
    valid
    & (snr >= threshold)
    & (snr == local_max)
)

y, x = np.where(detections)

# Convert pixel coordinates to celestial coordinates
sky = wcs.pixel_to_world(x, y)

catalogue = pd.DataFrame({
    "pixel_x": x,
    "pixel_y": y,
    "ra_deg": sky.ra.deg,
    "dec_deg": sky.dec.deg,
    "flux_mjy_sr": image[y, x],
    "variance": variance[y, x],
    "snr": snr[y, x]
})

catalogue = catalogue.sort_values(
    "snr",
    ascending=False
)

catalogue.to_csv(
    "data/processed/source_candidates.csv",
    index=False
)

print("\nCOSMIC ECHO | SOURCE DETECTION")
print("-" * 45)
print("Valid pixels:", np.count_nonzero(valid))
print("Candidate detections:", len(catalogue))
print("\nTop 10 candidates:")
print(catalogue.head(10).to_string(index=False))
print("\nCatalogue saved.")
