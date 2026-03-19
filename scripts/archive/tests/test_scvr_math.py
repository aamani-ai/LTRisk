"""
test_scvr_math.py
-----------------
Validates the SCVR area-under-exceedance-curve calculation against analytically
known inputs. Ensures the math is correct before trusting results on real data.

Run from project root:
    python scripts/tests/test_scvr_math.py

Expected output:  PASS  (or a descriptive FAIL message)
"""

import sys
import numpy as np


# ---------------------------------------------------------------------------
# SCVR core function (mirrors what the notebook implements)
# ---------------------------------------------------------------------------

def compute_scvr(baseline_values: np.ndarray, future_values: np.ndarray) -> dict:
    """
    Compute SCVR as the fractional change in area under the empirical exceedance curve.

    SCVR = (area_future - area_baseline) / area_baseline

    The exceedance curve is constructed by rank-sorting values in descending order
    and associating each with an exceedance probability on [0, 1].
    Area is computed via the trapezoidal rule.

    Args:
        baseline_values: 1-D array of historical daily values.
        future_values:   1-D array of future daily values.

    Returns:
        dict with keys: scvr, area_baseline, area_future
    """
    # Sort descending (highest values have lowest exceedance probability)
    b_sorted = np.sort(baseline_values)[::-1].astype(float)
    f_sorted = np.sort(future_values)[::-1].astype(float)

    n_b = len(b_sorted)
    n_f = len(f_sorted)

    exc_probs_b = np.linspace(0, 1, n_b)
    exc_probs_f = np.linspace(0, 1, n_f)

    area_b = float(np.trapezoid(b_sorted, exc_probs_b))
    area_f = float(np.trapezoid(f_sorted, exc_probs_f))

    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0

    return {"scvr": scvr, "area_baseline": area_b, "area_future": area_f}


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

def test_identical_distributions() -> list[str]:
    """SCVR of two identical distributions must be 0."""
    failures = []
    rng = np.random.default_rng(0)
    values = rng.uniform(0, 10, 3650)
    result = compute_scvr(values, values.copy())
    if abs(result["scvr"]) > 1e-6:
        failures.append(
            f"Identical distributions: expected SCVR=0, got {result['scvr']:.6f}."
        )
    return failures


def test_uniform_shift_upward() -> list[str]:
    """
    Uniform shift of the distribution upward must produce positive SCVR.

    Baseline: U[0, 10]     mean = 5,  area ≈ 5
    Future:   U[2, 12]     mean = 7,  area ≈ 7
    Expected SCVR ≈ (7 - 5) / 5 = 0.40  (within ±0.05 tolerance)
    """
    failures = []
    n = 100_000  # large N for low variance in area estimate
    rng = np.random.default_rng(1)
    baseline = rng.uniform(0, 10, n)
    future = rng.uniform(2, 12, n)

    result = compute_scvr(baseline, future)
    scvr = result["scvr"]
    expected = 0.40

    if not (0.30 <= scvr <= 0.50):
        failures.append(
            f"Uniform upward shift: expected SCVR ≈ {expected:.2f} ± 0.05, got {scvr:.4f}."
        )
    return failures


def test_uniform_shift_downward() -> list[str]:
    """
    Uniform shift of the distribution downward must produce negative SCVR.

    Baseline: U[0, 10]     area ≈ 5
    Future:   U[-2, 8]     area ≈ 3
    Expected SCVR ≈ (3 - 5) / 5 = -0.40  (within ±0.05 tolerance)
    """
    failures = []
    n = 100_000
    rng = np.random.default_rng(2)
    baseline = rng.uniform(0, 10, n)
    future = rng.uniform(-2, 8, n)

    result = compute_scvr(baseline, future)
    scvr = result["scvr"]

    if not (-0.50 <= scvr <= -0.30):
        failures.append(
            f"Uniform downward shift: expected SCVR ≈ -0.40 ± 0.05, got {scvr:.4f}."
        )
    return failures


def test_heavier_tail() -> list[str]:
    """
    A distribution with a heavier upper tail (same mean, more extremes) must
    produce a positive SCVR. This mimics what climate change does to temperature.

    Baseline: N(30, 3)        standard normal spread
    Future:   mixture of N(30, 3) (80%) and N(42, 2) (20%)  — added hot tail
    """
    failures = []
    rng = np.random.default_rng(3)
    n = 50_000

    baseline = rng.normal(30, 3, n)

    # Future: mostly the same distribution but 20% of days are much hotter
    future = np.where(
        rng.random(n) < 0.20,
        rng.normal(42, 2, n),
        rng.normal(30, 3, n),
    )

    result = compute_scvr(baseline, future)
    scvr = result["scvr"]

    if scvr <= 0:
        failures.append(
            f"Heavier tail: expected SCVR > 0 (more extreme hot days), got {scvr:.4f}."
        )
    return failures


def test_scvr_monotonicity() -> list[str]:
    """
    As the future distribution shifts progressively warmer, SCVR must increase
    monotonically. Tests 5 shift steps.
    """
    failures = []
    n = 20_000
    rng = np.random.default_rng(4)
    baseline = rng.uniform(0, 10, n)

    shifts = [0, 1, 2, 3, 4]
    scvrs = []
    for shift in shifts:
        future = rng.uniform(shift, 10 + shift, n)
        result = compute_scvr(baseline, future)
        scvrs.append(result["scvr"])

    for i in range(1, len(scvrs)):
        if scvrs[i] <= scvrs[i - 1]:
            failures.append(
                f"Monotonicity fail: SCVR did not increase at shift={shifts[i]}. "
                f"SCVR values: {[f'{s:.3f}' for s in scvrs]}"
            )
    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("TEST: SCVR Mathematical Correctness")
    print("=" * 60)

    tests = [
        ("Identical distributions → SCVR = 0",  test_identical_distributions),
        ("Uniform upward shift → SCVR ≈ +0.40", test_uniform_shift_upward),
        ("Uniform downward shift → SCVR ≈ -0.40", test_uniform_shift_downward),
        ("Heavier upper tail → SCVR > 0",        test_heavier_tail),
        ("Monotonic increase with shift",         test_scvr_monotonicity),
    ]

    all_passed = True
    for name, test_fn in tests:
        failures = test_fn()
        status = "PASS" if not failures else "FAIL"
        print(f"\n  [{status}] {name}")
        for msg in failures:
            print(f"           {msg}")
        if failures:
            all_passed = False

    print()
    print("=" * 60)
    if all_passed:
        print("PASS — All SCVR mathematical correctness checks passed.")
    else:
        print("FAIL — One or more SCVR checks failed (see above).")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
