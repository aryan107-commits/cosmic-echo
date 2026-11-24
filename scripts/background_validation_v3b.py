
import numpy as np
from astropy.stats import sigma_clip
from pathlib import Path

print("\nCOSMIC ECHO | V3B SOURCE-FREE VALIDATION")
print("-" * 50)

data = np.load("data/processed/photutils_background_v2.npz")

corrected = data["corrected"]
rms = data["background_rms"]
mask = data["combined_mask"].astype(bool)

# Select finite, unmasked pixels
valid = (
    np.isfinite(corrected)
    & np.isfinite(rms)
    & (rms > 0)
    & (~mask)
)

residual = corrected[valid]
normalized = residual / rms[valid]

print("\nINITIAL SAMPLE")
print("Valid pixels:", residual.size)

# Robust sigma clipping
clipped = sigma_clip(
    normalized,
    sigma=3.0,
    maxiters=5,
    cenfunc="median",
    stdfunc="mad_std"
)

clean = clipped.compressed()

if clean.size == 0:
    raise ValueError("No pixels remain after sigma clipping.")

# Calculate statistics
median = np.median(clean)
sigma = 1.4826 * np.median(np.abs(clean - median))

print("\nSOURCE-FREE CANDIDATE STATISTICS")
print("Remaining pixels:", clean.size)
print("Rejected pixels:", normalized.size - clean.size)
print("Normalized median:", median)
print("Normalized robust sigma:", sigma)

print("\nINTERPRETATION")

if abs(median) < 0.1 and 0.8 <= sigma <= 1.2:
    print("Noise model is consistent with the nominal RMS.")
elif sigma > 1.2:
    print("Residual noise remains above nominal RMS.")
else:
    print("Further investigation of bias and noise model is needed.")

# Save results
np.savez_compressed(
    "data/processed/v3b_validation_report.npz",
    normalized_median=median,
    normalized_sigma=sigma,
    remaining_pixels=clean.size,
    rejected_pixels=normalized.size-clean.size
)

print("\nReport saved:")
print("data/processed/v3b_validation_report.npz")

print("\nV3B VALIDATION COMPLETE")
