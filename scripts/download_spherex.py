import pandas as pd
import shutil
from pathlib import Path
from astropy.io import fits
from astropy.utils.data import download_file

print("COSMIC ECHO | FIRST IMAGE RETRIEVAL")
print("=" * 45)

# Load archive metadata
df = pd.read_csv("data/spherex_search_results.csv")

# Select first D1 observation
selected = df[df["energy_bandpassname"] == "SPHEREx-D1"].iloc[0]

url = selected["access_url"]

print("Observation ID:", selected["obs_id"])
print("Spectral band:", selected["energy_bandpassname"])
print("Downloading FITS file...")

# Download one image
downloaded_file = download_file(
    url,
    cache=True,
    show_progress=True
)

# Store it inside the project
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "first_spherex_image.fits"
shutil.copy2(downloaded_file, output_file)

print("\nDownload complete:", output_file)

# Inspect FITS structure
print("\nFITS CONTENTS:")
with fits.open(output_file, memmap=True) as hdul:
    hdul.info()

print("\nFirst SPHEREx image retrieved successfully.")