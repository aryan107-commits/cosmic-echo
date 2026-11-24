
import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from scipy.ndimage import zoom, distance_transform_edt

IMAGE_FILE = "data/raw/first_spherex_image.fits"
MASK_FILE = "data/processed/quality_masks.npz"

# Load original science image and zodiacal model
with fits.open(IMAGE_FILE) as hdul:
    image = hdul["IMAGE"].data.astype(float)
    zodi = hdul["ZODI"].data.astype(float)

# Diagnostic residual
residual = image - zodi

# Load provisional quality masks
with np.load(MASK_FILE) as masks:
    hard_mask = masks["hard_mask"]
    artifact_mask = masks["artifact_mask"]
    transient_mask = masks["transient_mask"]

# Exclude invalid and flagged pixels from background estimation
valid = (
    np.isfinite(residual)
    & ~hard_mask
    & ~artifact_mask
    & ~transient_mask
)

# Divide image into 64 x 64 pixel cells
cell_size = 64
height, width = residual.shape

ny = int(np.ceil(height / cell_size))
nx = int(np.ceil(width / cell_size))

background_grid = np.full((ny, nx), np.nan)

for gy in range(ny):
    for gx in range(nx):
        y0 = gy * cell_size
        y1 = min(y0 + cell_size, height)
        x0 = gx * cell_size
        x1 = min(x0 + cell_size, width)

        tile = residual[y0:y1, x0:x1]
        tile_valid = valid[y0:y1, x0:x1]

        values = tile[tile_valid]

        if len(values) >= 20:
            background_grid[gy, gx] = np.median(values)

# Fill empty grid cells using nearest valid grid cell
missing = ~np.isfinite(background_grid)

if np.all(missing):
    raise ValueError("No valid background grid cells.")

if np.any(missing):
    nearest = distance_transform_edt(
        missing,
        return_distances=False,
        return_indices=True
    )
    background_grid[missing] = background_grid[
        tuple(index[missing] for index in nearest)
    ]

# Interpolate background grid to full image size
background_map = zoom(
    background_grid,
    (height / ny, width / nx),
    order=1
)

background_map = background_map[:height, :width]

# Diagnostic background-subtracted image
corrected = residual - background_map

# Save numerical products
np.savez_compressed(
    "data/processed/background_estimate.npz",
    background_grid=background_grid,
    background_map=background_map,
    corrected=corrected
)

# Plot diagnostic panels
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

panels = [
    (residual, "IMAGE - ZODI"),
    (background_map, "Estimated Local Background"),
    (corrected, "Diagnostic Corrected Image")
]

for ax, (data, title) in zip(axes, panels):
    values = data[np.isfinite(data)]
    vmin, vmax = np.percentile(values, [2, 98])

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
    "data/processed/background_estimation.png",
    dpi=200
)

plt.show()

print("COSMIC ECHO | LOCAL BACKGROUND ESTIMATION")
print("------------------------------------------")
print("Grid shape:", background_grid.shape)
print("Valid estimation cells:", np.count_nonzero(~missing))
print("Background median:", np.median(background_map))
print("Corrected image median:", np.median(corrected))
print("Saved background_estimate.npz")
