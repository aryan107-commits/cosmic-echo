import numpy as np
from astropy.io import fits

file_path = "data/raw/first_spherex_image.fits"

with fits.open(file_path) as hdul:

    flags = hdul["FLAGS"].data.astype(np.uint32)
    header = hdul["FLAGS"].header

    total_pixels = flags.size

    print("\nCOSMIC ECHO | FLAG ANALYSIS")
    print("-" * 55)

    print("Image shape:", flags.shape)
    print("Total pixels:", total_pixels)

    print("\nFLAG DISTRIBUTION")
    print("-" * 55)

    for i in range(32):

        name = header.get(f"MSKN{i:04d}")
        mask = header.get(f"MSKM{i:04d}")

        if name is None or mask is None:
            continue

        count = np.count_nonzero(
            np.bitwise_and(flags, np.uint32(mask))
        )

        percentage = (count / total_pixels) * 100

        print(
            f"{name.strip():15s} "
            f"{count:10,d} pixels "
            f"({percentage:.4f}%)"
        )

    print("-" * 55)
    print("Flag analysis completed.")