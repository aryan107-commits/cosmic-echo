
import numpy as np
from astropy.io import fits

print("\nCOSMIC ECHO | V3D INSTRUMENT DIAGNOSTICS")
print("=" * 55)

path = "data/raw/first_spherex_image.fits"

# Inspect every FITS extension
with fits.open(path) as hdul:

    print("\nFITS STRUCTURE")
    hdul.info()

    for i, hdu in enumerate(hdul):
        print(f"\nHDU {i}: {hdu.name}")

        if hdu.header:
            for key in [
                "BUNIT", "TELESCOP", "INSTRUME",
                "FILTER", "WAVELEN", "EXPTIME",
                "GAIN", "BUNIT", "BTYPE",
                "NAXIS", "BZERO", "BSCALE"
            ]:
                if key in hdu.header:
                    print(key, ":", hdu.header[key])

        if hdu.data is not None:
            print("Data shape:", hdu.data.shape)
            print("Data type:", hdu.data.dtype)

# Load V2 products
data = np.load("data/processed/photutils_background_v2.npz")

corrected = data["corrected"]
rms = data["background_rms"]
mask = data["combined_mask"].astype(bool)

valid = (
    np.isfinite(corrected)
    & np.isfinite(rms)
    & (rms > 0)
    & (~mask)
)

normalized = np.full(corrected.shape, np.nan)
normalized[valid] = corrected[valid] / rms[valid]

# Analyze spatial tiles
tile_size = 204

records = []

for y in range(0, 2040, tile_size):
    for x in range(0, 2040, tile_size):

        tile = normalized[
            y:y + tile_size,
            x:x + tile_size
        ]

        tile_valid = valid[
            y:y + tile_size,
            x:x + tile_size
        ]

        values = tile[tile_valid]

        if values.size < 100:
            continue

        median = np.median(values)

        sigma = 1.4826 * np.median(
            np.abs(values - median)
        )

        records.append((
            y, x, values.size,
            median, sigma
        ))

records.sort(key=lambda r: r[4], reverse=True)

print("\nTOP 10 HIGHEST NOISE TILES")
print("Y, X, Pixels, Median, Robust Sigma")

for record in records[:10]:
    print(record)

print("\nTOP 10 LOWEST NOISE TILES")

for record in sorted(records, key=lambda r: r[4])[:10]:
    print(record)

print("\nV3D DIAGNOSTICS COMPLETE")
   