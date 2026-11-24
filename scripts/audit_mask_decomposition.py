from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


DEFAULT_NPZ = "data/processed/photutils_background_v2.npz"
DEFAULT_FITS = "data/raw/first_spherex_image.fits"


def pct(count, total):
    return 100.0 * count / total if total else float("nan")


def edge_distance(shape):
    ny, nx = shape

    y = np.arange(ny)[:, None]
    x = np.arange(nx)[None, :]

    return np.minimum(
        np.minimum(y, ny - 1 - y),
        np.minimum(x, nx - 1 - x)
    )


def robust_sigma(values):
    values = np.asarray(values)
    values = values[np.isfinite(values)]

    if values.size == 0:
        return float("nan")

    median = np.median(values)

    return 1.4826 * np.median(
        np.abs(values - median)
    )


def validate_masks(source, combined):

    print("\n[1] MASK VALIDATION")
    print("=" * 65)

    print("Image shape:", source.shape)
    print("Total pixels:", source.size)

    print("Source mask unique values:", np.unique(source))
    print("Combined mask unique values:", np.unique(combined))

    if source.shape != combined.shape:
        raise ValueError("Mask dimensions do not match.")

    extra = combined & ~source

    missing = source & ~combined

    print("\nSource mask coverage:",
          f"{pct(source.sum(), source.size):.6f}%")

    print("Combined mask coverage:",
          f"{pct(combined.sum(), combined.size):.6f}%")

    print("Extra pixels:",
          int(extra.sum()))

    print("Extra coverage:",
          f"{pct(extra.sum(), extra.size):.6f}%")

    print("Source pixels missing from combined:",
          int(missing.sum()))

    if missing.sum() == 0:
        print("Result: combined_mask is a superset of source_mask.")
    else:
        print("WARNING: combined_mask is not a superset.")

    return extra


def report_geometry(extra):

    print("\n[2] EXTRA MASK GEOMETRY")
    print("=" * 65)

    if not extra.any():
        print("Extra mask is empty.")
        return

    ny, nx = extra.shape

    row_fraction = extra.mean(axis=1)
    col_fraction = extra.mean(axis=0)

    print("Rows containing extra pixels:",
          int((row_fraction > 0).sum()), "/", ny)

    print("Fully masked rows:",
          int((row_fraction >= 0.999).sum()))

    print("Columns containing extra pixels:",
          int((col_fraction > 0).sum()), "/", nx)

    print("Fully masked columns:",
          int((col_fraction >= 0.999).sum()))

    ys, xs = np.where(extra)

    print("Bounding box:")
    print("y:", int(ys.min()), "to", int(ys.max()))
    print("x:", int(xs.min()), "to", int(xs.max()))

    distance = edge_distance(extra.shape)
    extra_distance = distance[extra]

    print("\nEDGE-BAND ANALYSIS")

    for quantile in (0.50, 0.90, 0.99):

        width = int(np.quantile(extra_distance, quantile)) + 1

        band = distance < width

        print(
            f"{quantile * 100:.0f}% of extra pixels "
            f"within {width} pixels of edge; "
            f"band purity: "
            f"{pct(extra[band].sum(), band.sum()):.3f}%"
        )

    try:
        from scipy.ndimage import label

        labels, component_count = label(extra)

        sizes = np.bincount(labels.ravel())[1:]
        sizes = np.sort(sizes)[::-1]

        print("\nCONNECTED COMPONENTS")
        print("Number of components:", component_count)
        print("Largest component sizes:", sizes[:10].tolist())

    except ImportError:
        print("SciPy unavailable; component analysis skipped.")


def report_layers(extra, layers, quantile=4.0):

    print("\n[3] IMAGE-LAYER QUANTILE ANALYSIS")
    print("=" * 65)

    for name, array in layers.items():

        if array.shape != extra.shape:
            print(name, ": shape mismatch; skipped.")
            continue

        finite = np.isfinite(array)

        extra_finite = extra & finite

        if not finite.any() or not extra_finite.any():
            print(name, ": no usable pixels.")
            continue

        values = array[finite]

        high_threshold = np.percentile(
            values, 100 - quantile
        )

        low_threshold = np.percentile(
            values, quantile
        )

        selected = array[extra_finite]

        print(f"\n{name}")

        print("Non-finite extra pixels:",
              int((extra & ~finite).sum()))

        print(
            f"Extra pixels above {100-quantile:.0f}th percentile:",
            f"{np.mean(selected >= high_threshold) * 100:.3f}%"
        )

        print(
            f"Extra pixels below {quantile:.0f}th percentile:",
            f"{np.mean(selected <= low_threshold) * 100:.3f}%"
        )

        print("Extra median:", np.median(selected))
        print("Extra robust sigma:", robust_sigma(selected))


def report_flags(extra, combined, flags, quality_bits):

    print("\n[4] FLAG BIT ANALYSIS")
    print("=" * 65)

    flags = np.asarray(flags).astype(np.uint32)

    print(
        "Bit | Image coverage | Extra coverage | "
        "Flag pixels in extra"
    )

    for bit_number in range(32):

        bit = (
            flags & (np.uint32(1) << np.uint32(bit_number))
        ) != 0

        if not bit.any():
            continue

        overlap = int((bit & extra).sum())

        print(
            f"{bit_number:3d} | "
            f"{pct(bit.sum(), bit.size):13.4f}% | "
            f"{pct(overlap, max(extra.sum(), 1)):13.4f}% | "
            f"{pct(overlap, bit.sum()):13.4f}%"
        )

    flagged_extra = (flags != 0) & extra

    print("\nExtra pixels with any flag:",
          f"{pct(flagged_extra.sum(), max(extra.sum(), 1)):.4f}%")

    if quality_bits:

        quality_mask = np.zeros(flags.shape, dtype=bool)

        for bit_number in quality_bits:

            if not 0 <= bit_number <= 31:
                raise ValueError(
                    f"Invalid flag bit: {bit_number}"
                )

            quality_mask |= (
                flags & (
                    np.uint32(1) << np.uint32(bit_number)
                )
            ) != 0

        print("\nSELECTED QUALITY FLAGS")

        print("Selected bits:", quality_bits)

        print("Quality mask coverage:",
              f"{pct(quality_mask.sum(), quality_mask.size):.6f}%")

        print("Quality pixels outside combined:",
              int((quality_mask & ~combined).sum()))

        print("Quality coverage outside combined:",
              f"{pct((quality_mask & ~combined).sum(), quality_mask.size):.6f}%")

        print("Quality pixels inside extra:",
              int((quality_mask & extra).sum()))


def report_corrected(corrected, source, combined):

    print("\n[5] CORRECTED IMAGE VALIDITY")
    print("=" * 65)

    nan_mask = ~np.isfinite(corrected)

    print("Non-finite pixels overall:",
          int(nan_mask.sum()))

    print("Non-finite overall coverage:",
          f"{pct(nan_mask.sum(), nan_mask.size):.6f}%")

    print("Non-finite inside combined:",
          int((nan_mask & combined).sum()))

    print("Non-finite outside combined:",
          int((nan_mask & ~combined).sum()))

    print("Non-finite inside source:",
          int((nan_mask & source).sum()))


def load_fits_layers(path):

    from astropy.io import fits

    layers = {}
    flags = None

    with fits.open(path, memmap=False) as hdul:

        for name in ("IMAGE", "VARIANCE", "ZODI"):

            if name in hdul and hdul[name].data is not None:

                layers[name] = np.asarray(
                    hdul[name].data,
                    dtype=np.float64
                )

        if "FLAGS" in hdul and hdul["FLAGS"].data is not None:

            flags = np.asarray(hdul["FLAGS"].data)

    return layers, flags


def main():

    parser = argparse.ArgumentParser(
        description="COSMIC ECHO V2 mask decomposition audit"
    )

    parser.add_argument(
        "--npz",
        default=DEFAULT_NPZ
    )

    parser.add_argument(
        "--fits",
        default=DEFAULT_FITS
    )

    parser.add_argument(
        "--source-key",
        default="source_mask"
    )

    parser.add_argument(
        "--combined-key",
        default="combined_mask"
    )

    parser.add_argument(
        "--quality-bits",
        default=""
    )

    args = parser.parse_args()

    npz_path = Path(args.npz)
    fits_path = Path(args.fits)

    print("\nCOSMIC ECHO | V2 MASK DECOMPOSITION AUDIT")
    print("=" * 65)

    if not npz_path.is_file():

        print("ERROR: NPZ file not found:", npz_path)
        return 2

    with np.load(npz_path) as archive:

        print("NPZ keys:", list(archive.keys()))

        if args.source_key not in archive:
            print("ERROR: source mask key missing.")
            return 2

        if args.combined_key not in archive:
            print("ERROR: combined mask key missing.")
            return 2

        source_raw = archive[args.source_key]
        combined_raw = archive[args.combined_key]

        if not np.all(np.isin(source_raw, [0, 1])):
            print("ERROR: source mask contains values other than 0 and 1.")
            return 2

        if not np.all(np.isin(combined_raw, [0, 1])):
            print("ERROR: combined mask contains values other than 0 and 1.")
            return 2

        source = source_raw.astype(bool)
        combined = combined_raw.astype(bool)

        corrected = (
            np.array(archive["corrected"])
            if "corrected" in archive
            else None
        )

    if source.shape != combined.shape:
        print("ERROR: mask dimensions differ.")
        return 2

    extra = validate_masks(source, combined)

    report_geometry(extra)

    layers = {}
    flags = None

    if fits_path.is_file():

        layers, flags = load_fits_layers(fits_path)

    else:

        print("\nWARNING: FITS file not found.")
        print("FITS-based diagnostics skipped.")

    if corrected is not None:

        if corrected.shape != source.shape:
            print("ERROR: corrected image dimensions differ.")
            return 2

        layers["CORRECTED"] = corrected.astype(np.float64)
        layers["ABS_CORRECTED"] = np.abs(corrected.astype(np.float64))

    if layers:
        report_layers(extra, layers)

    if flags is not None:

        if flags.shape == extra.shape:

            quality_bits = [
                int(bit.strip())
                for bit in args.quality_bits.split(",")
                if bit.strip()
            ]

            report_flags(
                extra,
                combined,
                flags,
                quality_bits
            )

        else:

            print("\nWARNING: FLAGS dimensions differ.")
            print("Flag diagnostics skipped.")

    if corrected is not None:

        report_corrected(
            corrected,
            source,
            combined
        )

    print("\n" + "=" * 65)
    print("AUDIT COMPLETE")
    print("Read-only execution: no files modified.")
    print("=" * 65)

    return 0


if __name__ == "__main__":
    sys.exit(main())
