
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

file_path = "data/raw/first_spherex_image.fits"

with fits.open(file_path) as hdul:
    image = hdul["IMAGE"].data.astype(float)
    zodi = hdul["ZODI"].data.astype(float)

# Diagnostic residual only; not a final background-subtracted image
residual = image - zodi

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

datasets = [
    (image, "Original IMAGE"),
    (zodi, "ZODI Model"),
    (residual, "IMAGE - ZODI (Diagnostic)")
]

for ax, (data, title) in zip(axes, datasets):
    valid = data[np.isfinite(data)]
    vmin, vmax = np.percentile(valid, [2, 98])

    ax.imshow(data, origin="lower", cmap="inferno",
              vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Pixel X")
    ax.set_ylabel("Pixel Y")

plt.tight_layout()
plt.savefig(
    "data/processed/background_components.png",
    dpi=200
)
plt.show()

print("COSMIC ECHO | BACKGROUND COMPONENTS")
print("-----------------------------------")

for name, data in [
    ("IMAGE", image),
    ("ZODI", zodi),
    ("RESIDUAL", residual)
]:
    valid = data[np.isfinite(data)]
    print(f"\n{name}")
    print("Median:", np.median(valid))
    print("99th percentile:", np.percentile(valid, 99))
