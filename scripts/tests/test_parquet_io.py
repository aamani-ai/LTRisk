"""
test_parquet_io.py
------------------
Validates that pyarrow is installed and that Parquet write/read round-trips work
correctly with the column schema defined in data/schema/cmip6_raw_schema.json.

Run from project root:
    python scripts/tests/test_parquet_io.py

Expected output:  PASS  (or a descriptive FAIL message)
"""

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "data" / "schema"

# ---------------------------------------------------------------------------
# Load schema
# ---------------------------------------------------------------------------
with open(SCHEMA_DIR / "cmip6_raw_schema.json") as f:
    SCHEMA = json.load(f)

COLUMN_SPEC = SCHEMA["columns"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_synthetic_dataframe(n_days: int = 365) -> pd.DataFrame:
    """
    Create a minimal synthetic DataFrame that matches cmip6_raw_schema.json.
    Uses realistic value ranges for Culberson TX (West Texas desert).
    """
    rng = np.random.default_rng(seed=42)
    dates = pd.date_range("2030-01-01", periods=n_days, freq="D")
    doy = dates.day_of_year

    # Seasonal cycle: summer peaks ~42°C, winter ~15°C for West Texas
    seasonal = np.sin(2 * np.pi * (doy - 80) / 365)  # peaks in summer

    tasmax = (32 + 12 * seasonal + rng.normal(0, 2, n_days)).astype("float32")
    tasmin = (18 + 10 * seasonal + rng.normal(0, 2, n_days)).astype("float32")
    tas = ((tasmax + tasmin) / 2).astype("float32")
    pr = np.maximum(0, rng.exponential(1.5, n_days)).astype("float32")
    sfcWind = np.maximum(0, rng.gamma(3, 2, n_days)).astype("float32")
    hurs = np.clip(30 + 15 * (-seasonal) + rng.normal(0, 8, n_days), 5, 95).astype("float32")
    rsds = np.maximum(0, (20 + 8 * seasonal + rng.normal(0, 2, n_days))).astype("float32")

    return pd.DataFrame({
        "date": dates,
        "year": dates.year.astype("int16"),
        "month": dates.month.astype("int8"),
        "doy": doy.astype("int16"),
        "tasmax": tasmax,
        "tasmin": tasmin,
        "tas": tas,
        "pr": pr,
        "sfcWind": sfcWind,
        "hurs": hurs,
        "rsds": rsds,
        "site_id": "hayhurst_solar",
        "scenario": "ssp245",
        "model": "MRI-ESM2-0",
    })


def check_dtype_compatibility(df: pd.DataFrame) -> list[str]:
    """Check that column dtypes are compatible with schema spec. Returns failure messages."""
    failures = []
    for col, spec in COLUMN_SPEC.items():
        if col not in df.columns:
            failures.append(f"Column '{col}' missing from DataFrame.")
            continue
        schema_dtype = spec["dtype"]
        actual_dtype = str(df[col].dtype)
        # Loose check: compatible families
        compat = {
            "datetime64[ns]": ["datetime64[ns]", "datetime64[us]", "datetime64[ms]"],
            "int16": ["int16", "int32", "int64"],
            "int8": ["int8", "int16", "int32", "int64"],
            "float32": ["float32", "float64"],
            # pandas stores Python str as object or ArrowDtype string
            "str": ["object", "string", "large_string[pyarrow]", "str"],
        }
        allowed = compat.get(schema_dtype, [schema_dtype])
        # Also accept if actual starts with any allowed prefix (handles pyarrow dtypes)
        if actual_dtype not in allowed and not any(actual_dtype.startswith(a) for a in allowed):
            failures.append(
                f"Column '{col}': schema expects {schema_dtype}, got {actual_dtype}."
            )
    return failures


def check_invariants(df: pd.DataFrame) -> list[str]:
    """Run invariant checks from the schema. Returns failure messages."""
    failures = []

    # tasmin <= tas <= tasmax
    if (df["tasmin"] > df["tasmax"]).any():
        n = (df["tasmin"] > df["tasmax"]).sum()
        failures.append(f"Invariant fail: tasmin > tasmax on {n} rows.")
    if (df["tas"] < df["tasmin"]).any() or (df["tas"] > df["tasmax"]).any():
        failures.append("Invariant fail: tas outside [tasmin, tasmax] range.")

    # Non-negative
    for col in ["pr", "sfcWind", "rsds"]:
        if (df[col] < 0).any():
            failures.append(f"Invariant fail: {col} has negative values.")

    # Humidity bounds
    if (df["hurs"] < 0).any() or (df["hurs"] > 100).any():
        failures.append("Invariant fail: hurs outside [0, 100].")

    # No duplicate dates
    if df["date"].duplicated().any():
        failures.append("Invariant fail: duplicate dates found.")

    return failures


def roundtrip_parquet(df: pd.DataFrame) -> tuple[pd.DataFrame, Path]:
    """Write df to a temp Parquet file and read it back. Returns (df_reloaded, path)."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
        tmp_path = Path(f.name)
    df.to_parquet(tmp_path, index=False, engine="pyarrow")
    df_back = pd.read_parquet(tmp_path, engine="pyarrow")
    return df_back, tmp_path


def main() -> None:
    print("=" * 60)
    print("TEST: Parquet I/O and Schema Compliance")
    print("=" * 60)

    # 1. Build synthetic DataFrame
    print("\n[1/4] Building synthetic DataFrame (365 rows)...")
    df = build_synthetic_dataframe(n_days=365)
    print(f"      Shape: {df.shape}   Columns: {list(df.columns)}")

    # 2. Check dtypes against schema
    print("[2/4] Checking column dtypes against cmip6_raw_schema.json...")
    dtype_failures = check_dtype_compatibility(df)
    if dtype_failures:
        for msg in dtype_failures:
            print(f"      FAIL: {msg}")
        sys.exit(1)
    print("      All dtype checks passed.")

    # 3. Check invariants
    print("[3/4] Checking data invariants (tasmin<=tas<=tasmax, non-neg, etc.)...")
    invariant_failures = check_invariants(df)
    if invariant_failures:
        for msg in invariant_failures:
            print(f"      FAIL: {msg}")
        sys.exit(1)
    print("      All invariant checks passed.")

    # 4. Parquet round-trip
    print("[4/4] Writing to Parquet and reading back...")
    try:
        df_back, tmp_path = roundtrip_parquet(df)
    except Exception as e:
        print(f"      FAIL — Parquet write/read error: {e}")
        sys.exit(1)

    # Check shape preserved
    if df_back.shape != df.shape:
        print(f"      FAIL — Shape changed: {df.shape} -> {df_back.shape}")
        tmp_path.unlink(missing_ok=True)
        sys.exit(1)

    # Check date column survived as datetime
    if not pd.api.types.is_datetime64_any_dtype(df_back["date"]):
        print(f"      FAIL — 'date' column dtype after reload: {df_back['date'].dtype}")
        tmp_path.unlink(missing_ok=True)
        sys.exit(1)

    # Check numeric values are close
    for col in ["tasmax", "tasmin", "tas", "pr", "sfcWind", "hurs", "rsds"]:
        if not np.allclose(df[col].values, df_back[col].values, rtol=1e-5, atol=1e-5):
            print(f"      FAIL — Numeric mismatch in column '{col}' after round-trip.")
            tmp_path.unlink(missing_ok=True)
            sys.exit(1)

    tmp_path.unlink(missing_ok=True)
    print(f"      Round-trip OK. File size was ~{tmp_path.stat().st_size if tmp_path.exists() else 'N/A'} bytes (already cleaned up).")

    print()
    print("=" * 60)
    print("PASS — Parquet I/O and schema compliance verified.")
    print("=" * 60)


if __name__ == "__main__":
    main()
