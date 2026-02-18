"""
Quick diagnostic: find which year in the future projection has all-null data.
Run from project root with venv activated:
    python scripts/tests/check_null_year.py
"""
import json
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
with open(REPO_ROOT / "data/schema/sites.json") as f:
    SITES = json.load(f)

SITE = SITES["hayhurst_solar"]
MODEL = SITE["open_meteo_model"]
path = REPO_ROOT / "data/raw/cmip6/hayhurst_solar" / f"ssp245_{MODEL}_2015_2050.parquet"

df = pd.read_parquet(path)

null_by_year = df.groupby("year")["tasmax"].apply(lambda x: x.isna().sum())
null_years = null_by_year[null_by_year > 0]

print(f"Future data shape: {df.shape}")
print(f"Total nulls in tasmax: {df['tasmax'].isna().sum()}")
print()
if len(null_years) == 0:
    print("No null years found.")
else:
    print("Years with null tasmax values:")
    print(null_years.to_string())
    print()
    # Check if it is ALL variables or just some
    null_year = null_years.index[0]
    yr_data = df[df["year"] == null_year]
    print(f"Sample rows for year {null_year} (first 3):")
    print(yr_data[["date", "tasmax", "tasmin", "pr", "sfcWind", "rsds"]].head(3).to_string())
