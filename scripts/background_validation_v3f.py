
import numpy as np
from astropy.io import fits

print("\nCOSMIC ECHO | V3F FLAG AND VARIANCE INVESTIGATION")
print("=" * 65)

fits_path = "data/raw/first_spherex_image.fits"
npz_path = "data/processed/photutils_background_v2.npz"

with fits.open(fits_path) as hdul:
    image = hdul["IMAGE"].data.astype(float)
    flags = hdul["FLAGS"].data.astype(np.uint32)
    variance = hdul["VARIANCE"].data.astype(float)
    zodi = hdul["ZODI"].data.astype(float)

    image_header = hdul["IMAGE"].header
    flag_header = hdul["FLAGS"].header
    variance_header = hdul["VARIANCE"].header

data = np.load(npz_path)
background_rms = data["background_rms"]
corrected = data["corrected"]
source_mask = data["source_mask"].astype(bool)
combined_mask = data["combined_mask"].astype(bool)

total = flags.size

# --------------------------------------------------
# 1. Official definitions stored in this FITS header
# --------------------------------------------------

print("\n1. FLAG DEFINITIONS FROM FITS HEADER")

definitions = []

for key in flag_header:
    if key.startswith("MSKN"):
        bit = int(key[4:])
        name = flag_header[key]
        description = flag_header.get(f"MSKD{bit:04d}", "No description")
        definitions.append((bit, name, description))

definitions.sort()

for bit, name, description in definitions:
    print(f"Bit {bit:2d} | {name:16s} | {description}")

# --------------------------------------------------
# 2. Individual bit coverage
# --------------------------------------------------

print("\n2. INDIVIDUAL FLAG BIT COVERAGE")
print("Bit | Name | Pixels | Coverage")

for bit, name, description in definitions:
    selected = (flags & (np.uint32(1) << np.uint32(bit))) != 0
    count = np.count_nonzero(selected)

    print(
        f"{bit:2d} | {name:16s} | "
        f"{count:10,} | {100 * count / total:8.3f}%"
    )

# --------------------------------------------------
# 3. Source flag versus our existing masks
# --------------------------------------------------

source_flag = (flags & (np.uint32(1) << np.uint32(21))) != 0

print("\n3. MASK OVERLAP")

for name, mask in [
    ("SOURCE flag", source_flag),
    ("Photutils source mask", source_mask),
    ("Combined mask", combined_mask),
]:
    print(f"{name:24s}: {mask.mean() * 100:.3f}%")

print(
    "SOURCE flag AND source mask:",
    np.mean(source_flag & source_mask) * 100,
    "%"
)

print(
    "SOURCE flag AND combined mask:",
    np.mean(source_flag & combined_mask) * 100,
    "%"
)

print(
    "SOURCE flag outside combined mask:",
    np.mean(source_flag & ~combined_mask) * 100,
    "%"
)

# --------------------------------------------------
# 4. Compare uncertainty estimates by SOURCE flag
# --------------------------------------------------

variance_valid = np.isfinite(variance) & (variance > 0)
rms_valid = np.isfinite(background_rms) & (background_rms > 0)
corrected_valid = np.isfinite(corrected)

variance_rms = np.full(variance.shape, np.nan)
variance_rms[variance_valid] = np.sqrt(variance[variance_valid])

valid = (
    variance_valid
    & rms_valid
    & corrected_valid
    & (~combined_mask)
)

ratio = variance_rms / background_rms
normalized = corrected / variance_rms

def robust_sigma(values):
    median = np.median(values)
    return 1.4826 * np.median(np.abs(values - median))

print("\n4. UNCERTAINTY COMPARISON BY SOURCE FLAG")

for name, selection in [
    ("SOURCE FLAG SET", source_flag),
    ("SOURCE FLAG NOT SET", ~source_flag),
]:
    selected = valid & selection

    r = ratio[selected]
    n = normalized[selected]

    print(f"\n{name}")
    print("Pixels:", selected.sum())

    if selected.sum() == 0:
        print("No valid pixels")
        continue

    print("Median variance/RMS ratio:", np.median(r))
    print("Median corrected/variance RMS:", np.median(n))
    print("Robust normalized scatter:", robust_sigma(n))

# --------------------------------------------------
# 5. SPHEREx processing metadata
# --------------------------------------------------

print("\n5. IMAGE PROCESSING COUNTS")

for key in image_header:
    if "L2 N_" in key:
        print(key, ":", image_header[key])

# --------------------------------------------------
# 6. Relevant extension metadata
# --------------------------------------------------

print("\n6. EXTENSION METADATA")

for name, header in [
    ("IMAGE", image_header),
    ("FLAGS", flag_header),
    ("VARIANCE", variance_header),
]:
    print(f"\n{name}")
    for key in [
        "BUNIT", "EXTTYPE", "VERSION",
        "DETECTOR", "OBSID", "DATE"
    ]:
        if key in header:
            print(key, ":", header[key])

# --------------------------------------------------
# 7. ZODI and image comparison
# --------------------------------------------------

print("\n7. ZODI COMPARISON")

valid_zodi = np.isfinite(zodi) & np.isfinite(image)
difference = image[valid_zodi] - zodi[valid_zodi]

print("Median IMAGE:", np.median(image[valid_zodi]))
print("Median ZODI:", np.median(zodi[valid_zodi]))
print("Median IMAGE - ZODI:", np.median(difference))

print("\nV3F COMPLETE")
