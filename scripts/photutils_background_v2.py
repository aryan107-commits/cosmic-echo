
import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.stats import SigmaClip

from photutils.background import (
    Background2D,
    MedianBackground
)

from photutils.segmentation import detect_sources

from scipy.ndimage import binary_dilation


# ============================================================
# 1. CONFIGURATION
# ============================================================

IMAGE_FILE = "data/raw/first_spherex_image.fits"
MASK_FILE = "data/processed/quality_masks.npz"
OLD_BACKGROUND_FILE = "data/processed/photutils_background.npz"

OUTPUT_FILE = "data/processed/photutils_background_v2.npz"
OUTPUT_IMAGE = "data/processed/photutils_background_v2.png"

BOX_SIZE = 64
FILTER_SIZE = 3

DETECTION_SIGMA = 5.0
MIN_SOURCE_PIXELS = 5
MASK_RADIUS = 3


# ============================================================
# 2. LOAD SPHEREX DATA
# ============================================================

print("\nCOSMIC ECHO | PHOTUTILS BACKGROUND V2")
print("--------------------------------------")

with fits.open(IMAGE_FILE) as hdul:
    image = hdul["IMAGE"].data.astype(float)
    zodi = hdul["ZODI"].data.astype(float)

residual = image - zodi

print("Image dimensions:", image.shape)


# ============================================================
# 3. LOAD QUALITY MASKS
# ============================================================

with np.load(MASK_FILE) as masks:

    base_mask = (
        masks["hard_mask"]
        | masks["artifact_mask"]
        | masks["transient_mask"]
    )

base_mask |= ~np.isfinite(residual)

print(
    "Base quality mask:",
    f"{np.mean(base_mask) * 100:.3f}%"
)


# ============================================================
# 4. LOAD INITIAL BACKGROUND MODEL
# ============================================================

with np.load(OLD_BACKGROUND_FILE) as old:

    old_background = old["background_map"]
    old_rms = old["background_rms"]

if not (
    residual.shape == old_background.shape == old_rms.shape
):
    raise ValueError("Image and background dimensions do not match.")

if not np.all(np.isfinite(old_background)):
    raise ValueError("Old background contains invalid values.")

if not np.all(np.isfinite(old_rms) & (old_rms > 0)):
    raise ValueError("Old RMS contains invalid or non-positive values.")


# ============================================================
# 5. SOURCE DETECTION
# ============================================================

threshold = old_background + DETECTION_SIGMA * old_rms

print("\nTHRESHOLD DIAGNOSTICS")
print("---------------------")

for name, data in [
    ("Residual", residual),
    ("Old background", old_background),
    ("Old RMS", old_rms),
    ("Threshold", threshold)
]:

    valid_data = data[np.isfinite(data)]

    print(
        name,
        np.percentile(valid_data, [0, 25, 50, 75, 99, 100])
    )

valid_pixels = (
    np.isfinite(residual)
    & np.isfinite(threshold)
    & ~base_mask
)

above_threshold = (
    valid_pixels
    & (residual > threshold)
)

print(
    "Valid pixels above threshold:",
    f"{np.mean(above_threshold) * 100:.3f}%"
)

segmentation = detect_sources(
    residual,
    threshold,
    n_pixels=MIN_SOURCE_PIXELS,
    mask=base_mask
)

if segmentation is None:
    raise RuntimeError(
        "No sources detected. Review the detection threshold."
    )

source_mask_raw = segmentation.data > 0

print("\nSOURCE DETECTION DIAGNOSTICS")
print("----------------------------")

print(
    "Raw source mask:",
    f"{np.mean(source_mask_raw) * 100:.3f}%"
)

print(
    "Detected segments:",
    segmentation.n_labels
)


# ============================================================
# 6. EXPAND SOURCE MASK
# ============================================================

radius = MASK_RADIUS

yy, xx = np.ogrid[-radius:radius + 1, -radius:radius + 1]

footprint = (
    xx**2 + yy**2 <= radius**2
)

source_mask = binary_dilation(
    source_mask_raw,
    structure=footprint
)

source_mask &= ~base_mask

print(
    "Expanded source mask:",
    f"{np.mean(source_mask) * 100:.3f}%"
)


# ============================================================
# 7. COMBINE MASKS
# ============================================================

combined_mask = base_mask | source_mask

print("\nMASK DIAGNOSTICS")
print("----------------")

print(
    "Base mask:",
    f"{np.mean(base_mask) * 100:.3f}%"
)

print(
    "Source mask:",
    f"{np.mean(source_mask) * 100:.3f}%"
)

print(
    "Combined mask:",
    f"{np.mean(combined_mask) * 100:.3f}%"
)


# ============================================================
# 8. CHECK MASK COVERAGE PER BACKGROUND BOX
# ============================================================

height, width = combined_mask.shape

fractions = []

for y in range(0, height - BOX_SIZE + 1, BOX_SIZE):

    for x in range(0, width - BOX_SIZE + 1, BOX_SIZE):

        box = combined_mask[
            y:y + BOX_SIZE,
            x:x + BOX_SIZE
        ]

        fractions.append(np.mean(box))

fractions = np.asarray(fractions)

print(
    "Median box masked:",
    f"{np.median(fractions) * 100:.3f}%"
)

print(
    "Maximum box masked:",
    f"{np.max(fractions) * 100:.3f}%"
)


# ============================================================
# 9. ESTIMATE BACKGROUND
# ============================================================

print("\nRUNNING PHOTUTILS BACKGROUND2D...")

bkg = Background2D(
    residual,
    box_size=(BOX_SIZE, BOX_SIZE),
    filter_size=(FILTER_SIZE, FILTER_SIZE),
    mask=combined_mask,
    sigma_clip=SigmaClip(
        sigma=3.0,
        maxiters=10
    ),
    bkg_estimator=MedianBackground(),
    exclude_percentile=30
)

background_map = bkg.background

background_rms = bkg.background_rms

corrected = residual - background_map


# ============================================================
# 10. SAVE NUMERICAL PRODUCTS
# ============================================================

np.savez_compressed(
    OUTPUT_FILE,
    background_map=background_map,
    background_rms=background_rms,
    source_mask=source_mask,
    corrected=corrected,
    combined_mask=combined_mask
)


# ============================================================
# 11. VISUALIZATION
# ============================================================

fig, axes = plt.subplots(
    2, 2,
    figsize=(14, 12)
)

panels = [
    (residual, "IMAGE - ZODI"),
    (source_mask.astype(float), "Detected Source Mask"),
    (background_map, "Source-masked Background"),
    (corrected, "Diagnostic Corrected Image")
]

for ax, (data, title) in zip(axes.flat, panels):

    valid = data[np.isfinite(data)]

    vmin, vmax = np.percentile(
        valid,
        [2, 98]
    )

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
    OUTPUT_IMAGE,
    dpi=200
)

plt.show()


# ============================================================
# 12. FINAL REPORT
# ============================================================

print("\nCOSMIC ECHO | BACKGROUND V2 REPORT")
print("-----------------------------------")

print("Detected segments:", segmentation.nlabels)

print(
    "Background median:",
    np.nanmedian(background_map)
)

print(
    "Background RMS median:",
    np.nanmedian(background_rms)
)

print(
    "Corrected median:",
    np.nanmedian(corrected)
)

print(
    "Invalid corrected pixels:",
    np.count_nonzero(~np.isfinite(corrected))
)

print("Numerical output:", OUTPUT_FILE)
print("Visualization:", OUTPUT_IMAGE)

print("\nBACKGROUND V2 EXECUTION COMPLETE")
