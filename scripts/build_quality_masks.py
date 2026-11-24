
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

INPUT_FILE = "data/raw/first_spherex_image.fits"
OUTPUT_DIR = "data/processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with fits.open(INPUT_FILE) as hdul:
    flags = hdul["FLAGS"].data.astype(np.uint32)
    header = hdul["FLAGS"].header

def get_flag(name):
    for i in range(32):
        flag_name = header.get(f"MSKN{i:04d}", "")
        if flag_name.strip() == name:
            return np.uint32(header[f"MSKM{i:04d}"])
    raise ValueError(f"Flag not found: {name}")

def combine_flags(names):
    result = np.zeros(flags.shape, dtype=bool)

    for name in names:
        result |= (flags & get_flag(name)) != 0

    return result

# Severe data-quality concerns
hard_flags = [
    "NONFUNC",
    "MISSING_DATA",
    "SUR_ERROR",
    "OVERFLOW",
    "NONLINEAR"
]

# Potential instrumental or processing artifacts
artifact_flags = [
    "CROSSTALK",
    "GHOST",
    "GHOST_FPA",
    "GHOST_EXT",
    "STREAK",
    "BLOOM",
    "SNOWBALL",
    "HALO",
    "PERSIST",
    "OUTLIER",
    "HOT",
    "COLD"
]

hard_mask = combine_flags(hard_flags)
artifact_mask = combine_flags(artifact_flags)

# Keep transient detections separate
transient_mask = combine_flags(["TRANSIENT"])

# Save all layers independently
np.savez_compressed(
    f"{OUTPUT_DIR}/quality_masks.npz",
    hard_mask=hard_mask,
    artifact_mask=artifact_mask,
    transient_mask=transient_mask
)

print("\nCOSMIC ECHO | QUALITY MASK REPORT")
print("-" * 45)

for name, mask in [
    ("Hard-quality flags", hard_mask),
    ("Artifact flags", artifact_mask),
    ("Transient flags", transient_mask)
]:
    count = np.count_nonzero(mask)
    percentage = 100 * count / mask.size

    print(f"{name}: {count:,} pixels ({percentage:.3f}%)")

# Visualize the three independent layers
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

layers = [
    (hard_mask, "Hard-quality flags"),
    (artifact_mask, "Artifact flags"),
    (transient_mask, "Transient flags")
]

for ax, (mask, title) in zip(axes, layers):
    ax.imshow(mask, origin="lower", cmap="gray_r")
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])

plt.suptitle("COSMIC ECHO | Provisional Quality Masks")
plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/quality_masks.png",
    dpi=180
)

plt.show()

print("\nQuality masks saved successfully.")
