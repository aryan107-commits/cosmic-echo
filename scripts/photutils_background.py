
import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.stats import SigmaClip
from photutils.background import (
    Background2D,
    MedianBackground
)

IMAGE_FILE = "data/raw/first_spherex_image.fits"
MASK_FILE = "data/processed/quality_masks.npz"

# Load science image and zodiacal model
with fits.open(IMAGE_FILE) as hdul:
    image = hdul["IMAGE"].data.astype(float)
    zodi = hdul["ZODI"].data.astype(float)

# Work on the diagnostic zodiacal-subtracted image
residual = image - zodi

# Load existing quality masks
with np.load(MASK_FILE) as masks:
    hard_mask = masks["hard_mask"]
    artifact_mask = masks["artifact_mask"]
    transient_mask = masks["transient_mask"]

# Combine masks and invalid pixels
mask = (
    hard_mask
    | artifact_mask
    | transient_mask
    | ~np.isfinite(residual)
)

# Configure robust background estimation
sigma_clip = SigmaClip(
    sigma=3.0,
    maxiters=10
)

background_estimator = MedianBackground()

bkg = Background2D(
    residual,
    box_size=(64, 64),
    filter_size=(3, 3),
    mask=mask,
    sigma_clip=sigma_clip,
    bkg_estimator=background_estimator,
    exclude_percentile=30
)

background_map = bkg.background
background_rms = bkg.background_rms

corrected = residual - background_map

# Save diagnostic products
np.savez_compressed(
    "data/processed/photutils_background.npz",
    background_map=background_map,
    background_rms=background_rms,
    corrected=corrected
)

# Visualize results
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

panels = [
    (residual, "IMAGE - ZODI"),
    (background_map, "Photutils Background"),
    (corrected, "Diagnostic Residual")
]

for ax, (data, title) in zip(axes, panels):
    valid = data[np.isfinite(data)]
    vmin, vmax = np.percentile(valid, [2, 98])

    ax.imshow(
        data,
        origin="lower",
        cmap="inferno",
        vmin=vmin,
        vmax=vmax
    )

    ax.set_title(title)
    ax.set_xlabel("Pixel X")
    ax.set_ylabel("Pixel Y")

plt.tight_layout()

plt.savefig(
    "data/processed/photutils_background.png",
    dpi=200
)

plt.show()

print("COSMIC ECHO | PHOTUTILS BACKGROUND")
print("-----------------------------------")
print("Background shape:", background_map.shape)
print("Median background:", np.median(background_map))
print("Median background RMS:", np.median(background_rms))
print("Corrected median:", np.nanmedian(corrected))
print("Invalid corrected pixels:", np.count_nonzero(~np.isfinite(corrected)))
print("Invalid corrected pixels:", np.count_nonzero(~np.isfinite(corrected)))
print("Saved diagnostic products.")
