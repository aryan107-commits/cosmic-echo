
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from pathlib import Path

# Load original image
with fits.open("data/raw/first_spherex_image.fits") as hdul:
    original = hdul["IMAGE"].data.astype(float)

# Load V2 arrays
data = np.load("data/processed/photutils_background_v2.npz")

background = data["background_map"]
rms = data["background_rms"]
source_mask = data["source_mask"].astype(bool)
corrected = data["corrected"]
combined_mask = data["combined_mask"].astype(bool)

# Robust visualization limits
def limits(image):
    valid = image[np.isfinite(image)]
    return np.percentile(valid, [2, 98])

# Create diagnostic figure
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

plots = [
    (original, "Original SPHEREx Image", "inferno"),
    (background, "Estimated Background", "viridis"),
    (rms, "Background RMS", "magma"),
    (corrected, "Background Corrected Image", "RdBu_r"),
    (source_mask, "Expanded Source Mask", "gray"),
    (combined_mask, "Combined Quality + Source Mask", "gray")
]

for ax, (image, title, cmap) in zip(axes.flat, plots):

    if image.dtype == bool:
        ax.imshow(image, cmap=cmap, origin="lower")
    else:
        vmin, vmax = limits(image)
        ax.imshow(
            image,
            cmap=cmap,
            origin="lower",
            vmin=vmin,
            vmax=vmax
        )

    ax.set_title(title)
    ax.set_xlabel("Pixel X")
    ax.set_ylabel("Pixel Y")

plt.suptitle(
    "COSMIC ECHO | Background Validation V3",
    fontsize=16
)

plt.tight_layout()

output = Path("data/processed/background_validation_v3.png")
output.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(output, dpi=180, bbox_inches="tight")
plt.show()

print("\nCOSMIC ECHO | V3 VISUALIZATION")
print("--------------------------------")
print("Source mask coverage:",
      round(np.mean(source_mask) * 100, 3), "%")

print("Combined mask coverage:",
      round(np.mean(combined_mask) * 100, 3), "%")

print("Visualization saved:", output)
print("\nV3 VISUALIZATION COMPLETE")
