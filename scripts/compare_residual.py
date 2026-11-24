
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

with fits.open("data/raw/first_spherex_image.fits") as hdul:
    image = hdul["IMAGE"].data.astype(float)
    zodi = hdul["ZODI"].data.astype(float)

residual = image - zodi

# Use identical intensity limits for IMAGE and residual
valid_image = image[np.isfinite(image)]
vmin, vmax = np.percentile(valid_image, [2, 98])

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

axes[0].imshow(
    image, origin="lower", cmap="inferno",
    vmin=vmin, vmax=vmax
)
axes[0].set_title("Original IMAGE")

axes[1].imshow(
    residual, origin="lower", cmap="inferno",
    vmin=vmin, vmax=vmax
)
axes[1].set_title("IMAGE - ZODI")

difference_limit = np.nanpercentile(
    np.abs(zodi[np.isfinite(zodi)]), 99
)

axes[2].imshow(
    zodi, origin="lower", cmap="coolwarm",
    vmin=-difference_limit, vmax=difference_limit
)
axes[2].set_title("ZODI Model")

for ax in axes:
    ax.set_xlabel("Pixel X")
    ax.set_ylabel("Pixel Y")

plt.tight_layout()
plt.savefig(
    "data/processed/residual_comparison.png",
    dpi=200
)
plt.show()

print("Median IMAGE:", np.nanmedian(image))
print("Median ZODI:", np.nanmedian(zodi))
print("Median RESIDUAL:", np.nanmedian(residual))
print("Residual saved.")
