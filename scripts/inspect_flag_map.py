import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

file_path = "data/raw/first_spherex_image.fits"

with fits.open(file_path) as hdul:
    flags = hdul["FLAGS"].data.astype(np.uint32)
    header = hdul["FLAGS"].header

flag_names = [
    "TRANSIENT",
    "OVERFLOW",
    "SUR_ERROR",
    "NONFUNC",
    "PERSIST",
    "OUTLIER",
    "CROSSTALK",
    "BLOOM",
    "SNOWBALL",
    "HALO"
]

fig, axes = plt.subplots(2, 5, figsize=(18, 8))

for ax, name in zip(axes.flat, flag_names):

    mask = None

    for i in range(32):
        if header.get(f"MSKN{i:04d}", "").strip() == name:
            mask = header[f"MSKM{i:04d}"]
            break

    if mask is None:
        ax.set_title(f"{name} - NOT FOUND")
        continue

    flagged = (flags & np.uint32(mask)) != 0

    ax.imshow(
        flagged,
        origin="lower",
        cmap="gray_r",
        interpolation="nearest"
    )

    ax.set_title(name)
    ax.set_xticks([])
    ax.set_yticks([])

plt.suptitle("COSMIC ECHO | SPHEREx Quality Flag Maps")
plt.tight_layout()

plt.savefig(
    "data/raw/flag_diagnostics.png",
    dpi=180
)

plt.show()

print("Flag diagnostic maps saved successfully.")