
from astroquery.ipac.irsa import Irsa
from astropy.coordinates import SkyCoord
from astropy import units as u
from pathlib import Path

# COSMIC ECHO - First SPHEREx archive query

print("=" * 50)
print("COSMIC ECHO | SPHEREx DATA EXPLORER")
print("=" * 50)

# Test coordinates from the official IRSA tutorial
ra_deg = 304.693508808
dec_deg = 42.4436872991

coordinate = SkyCoord(ra_deg, dec_deg, unit="deg")
search_radius = 1 * u.arcsec

print("\nConnecting to NASA/IPAC IRSA...")

# Search current public SPHEREx collections
results = Irsa.query_sia(
    pos=(coordinate, search_radius),
    collection=["spherex_dr1", "spherex_qr3"]
)

print(f"\nObservations found: {len(results)}")

# Save search results
output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

if len(results) > 0:
    output_file = output_dir / "spherex_search_results.csv"

    results.write(
        output_file,
        format="ascii.csv",
        overwrite=True
    )

    print("\nFirst observation:")
    print("RA:", results["s_ra"][0])
    print("DEC:", results["s_dec"][0])
    print("Observation ID:", results["obs_id"][0])
    print("Data URL:", results["access_url"][0])

    print(f"\nMetadata saved to: {output_file}")

else:
    print("No observations found at these coordinates.")

print("\nCOSMIC ECHO archive query completed.")
