import numpy as np
from astropy.io import fits

file_path = "data/raw/first_spherex_image.fits"

with fits.open(file_path) as hdul:
    for name in ["IMAGE", "ZODI", "VARIANCE"]:
        data = hdul[name].data.astype(float)
        valid = data[np.isfinite(data)]

        print(f"\n{name}")
        print("-" * 35)
        print("Median:", np.median(valid))
        print("Mean:", np.mean(valid))
        print("Std:", np.std(valid))
        print("Percentiles:")
        print(np.percentile(valid, [1, 25, 50, 75, 99]))