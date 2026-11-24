import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

file_path = "data/raw/first_spherex_image.fits"

with fits.open(file_path) as hdul:
    image = hdul["IMAGE"].data.astype(float)

# Ignore invalid pixels for display scaling
valid = image[np.isfinite(image)]

vmin, vmax = np.percentile(valid, [2, 98])

plt.figure(figsize=(10, 8))

plt.imshow(
    image,
    origin="lower",
    cmap="inferno",
    vmin=vmin,
    vmax=vmax
)

plt.colorbar(label="Calibrated flux (MJy/sr)")
plt.title("COSMIC ECHO | SPHEREx D1 Observation")
plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")

plt.tight_layout()
plt.savefig("data/raw/first_spherex_image.png", dpi=150)
plt.show()

print("Image visualization saved successfully.")