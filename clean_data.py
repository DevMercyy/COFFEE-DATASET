"""
Clean the raw coffee CSVs and save tidy versions to data/clean/.

Fixes applied (each one found by inspecting the raw files):
  1. Country names in the importer files have leading spaces ("   Austria").
  2. Production year headers have typos ("1990/20991", "2009/200"); they are
     renamed to the starting year of the crop year ("1990" ... "2019").
  3. Production carries pre-computed summary columns (Total/Average/Highest/
     Lowest); they are dropped and recomputed when needed.
  4. Brazil's exports for 2014, 2015 and 2019 are -2,147,483,648, the smallest
     32-bit integer (an overflow error in the source). They become missing.
  5. Zeros before a country starts reporting (e.g. Belgium and Luxembourg were
     reported together as "Belgium/Luxembourg" until 1998, Baltic states start
     in 1992) mean "not reported", not "no coffee". Leading zeros, and the
     Belgium/Luxembourg zeros from 1999 on, become missing.

Outputs, one wide and one long file per dataset:
  data/clean/<name>_wide.csv   Country, [Coffee_type], 1990 ... 2019
  data/clean/coffee_long.csv   dataset, Country, Coffee_type, Year, Value
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"

YEARS = [str(y) for y in range(1990, 2020)]

FILES = {
    "import": "Coffee_import.csv",
    "consumption": "Coffee_importers_consumption.csv",
    "re_export": "Coffee_re_export.csv",
    "export": "Coffee_export.csv",
    "production": "Coffee_production.csv",
}

INT32_MIN = -2_147_483_648


def blank_leading_zeros(row):
    """Replace zeros before the first non-zero value with NaN."""
    values = row.to_numpy(dtype=float, copy=True)
    nonzero = np.flatnonzero(values)
    if len(nonzero) == 0:
        return pd.Series(np.nan, index=row.index)
    values[: nonzero[0]] = np.nan
    return pd.Series(values, index=row.index)


def clean(name, filename):
    df = pd.read_csv(RAW / filename)
    df["Country"] = df["Country"].str.strip()

    if name == "production":
        crop_years = [c for c in df.columns if "/" in c and c != "Coffee type"]
        df = df.rename(columns=dict(zip(crop_years, YEARS)))
        df = df.rename(columns={"Coffee type": "Coffee_type"})
        df = df[["Country", "Coffee_type"] + YEARS]
    else:
        df = df[["Country"] + YEARS]

    values = df[YEARS].astype(float)
    overflow = values == INT32_MIN
    if overflow.any().any():
        for i, year in zip(*np.nonzero(overflow.to_numpy())):
            print(f"  {name}: {df['Country'].iat[i]} {YEARS[year]} is an overflow value, set to missing")
        values = values.mask(overflow)

    values = values.apply(blank_leading_zeros, axis=1)
    # Belgium/Luxembourg stops being reported in 1999, when the two countries
    # start appearing separately; its later zeros are also "not reported".
    combined = df["Country"] == "Belgium/Luxembourg"
    values.loc[combined, YEARS[9:]] = np.nan
    df[YEARS] = values
    return df


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    long_frames = []
    for name, filename in FILES.items():
        df = clean(name, filename)
        df.to_csv(CLEAN / f"{name}_wide.csv", index=False)
        id_cols = ["Country", "Coffee_type"] if "Coffee_type" in df else ["Country"]
        long = df.melt(id_vars=id_cols, value_vars=YEARS, var_name="Year", value_name="Value")
        long.insert(0, "dataset", name)
        long_frames.append(long)
        print(f"{name}: {len(df)} countries, {int(df[YEARS].isna().sum().sum())} missing cells")

    coffee_long = pd.concat(long_frames, ignore_index=True)
    coffee_long["Year"] = coffee_long["Year"].astype(int)
    coffee_long.to_csv(CLEAN / "coffee_long.csv", index=False)
    print(f"Saved cleaned files to {CLEAN}")


if __name__ == "__main__":
    main()
